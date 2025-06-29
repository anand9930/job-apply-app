from dataclasses import dataclass
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import time
import random
import json
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Optional, Union
import utils, dbutils


@dataclass
class JobData:
    job_id: int
    company_name: str
    location: str
    job_title: str
    job_link: str
    job_description: str
    job_criteria: str
    job_posted_date: str



class ScraperConfig:
    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    JOBS_PER_PAGE = 25
    MIN_DELAY = 2
    MAX_DELAY = 5
    RATE_LIMIT_DELAY = 30
    RATE_LIMIT_THRESHOLD = 10

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
        "Cache-Control": "no-cache",
    }


class LinkedInJobsScraper:
    def __init__(self):
        self.session = self._setup_session()

    def _setup_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    def _build_search_url(
        self,
        keywords: str,
        location: str,
        start: int = 0,
        f_AL: Optional[bool] = None,
        f_E: Optional[Union[int, list[int]]] = None,
        f_JT: Optional[Union[str, list[str]]] = None,
        f_WT: Optional[Union[int, list[int]]] = None,
        f_JIYN: Optional[bool] = None,
        f_PP: Optional[str] = None,
        f_C: Optional[str] = None,
        f_TPR: Optional[str] = None,
    ) -> str:
        params = {
            "keywords": keywords,
            "location": location,
            "start": start,
        }

        if f_AL:
            params["f_AL"] = "true"
        if f_JIYN:
            params["f_JIYN"] = "true"
        if f_E is not None:
            if isinstance(f_E, list):
                params["f_E"] = ",".join(str(e) for e in f_E)
            else:
                params["f_E"] = str(f_E)
        if f_JT is not None:
            if isinstance(f_JT, list):
                params["f_JT"] = ",".join(f_JT)
            else:
                params["f_JT"] = f_JT
        if f_WT is not None:
            if isinstance(f_WT, list):
                params["f_WT"] = ",".join(str(wt) for wt in f_WT)
            else:
                params["f_WT"] = str(f_WT)
        if f_PP:
            params["f_PP"] = f_PP
        if f_C:
            params["f_C"] = f_C
        if f_TPR:
            params["f_TPR"] = f_TPR

        query = '&'.join(f'{k}={quote(str(v))}' for k, v in params.items())
        return f"{ScraperConfig.BASE_URL}?{query}"
    
    def build_job_api_url(self,job_id: str) -> str:
        return f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"


    def _clean_job_url(self, url: str) -> str:
        return url.split("?")[0] if "?" in url else url

    def _extract_job_data(self, job_card: BeautifulSoup) -> Optional[JobData]:
        try:
            job_title = job_card.find("h3", class_="base-search-card__title").text.strip()
            company_name = job_card.find(
                "h4", class_="base-search-card__subtitle"
            ).text.strip()
            location = job_card.find(
                "span", class_="job-search-card__location"
            ).text.strip()
            job_link = self._clean_job_url(
                job_card.find("a", class_="base-card__full-link")["href"]
            )
            job_id=job_link.split("-")[-1]
            job_posted_date = job_card.find("time", class_="job-search-card__listdate")
            job_posted_date = job_posted_date.text.strip() if job_posted_date else "N/A"
            job_link_url=self.build_job_api_url(job_id)
            print(job_link_url)

            soup = self._fetch_job_page(job_link_url)
            job_description = soup.find("div", class_="description__text").text.strip()
            job_criteria = soup.find("ul", class_="description__job-criteria-list").text.strip()
            job_posted_date=soup.find("span", class_="posted-time-ago__text").text.strip()

            return JobData(
                job_id=job_id,
                company_name=company_name,
                location=location,
                job_title=job_title,
                job_link=job_link,
                job_description=job_description,
                job_criteria=job_criteria,
                job_posted_date=utils.linkedin_to_pgdate(job_posted_date)
            )
        except Exception as e:
            print(f"Failed to extract job data: {str(e)}")
            return None

    def _fetch_job_page(self, url: str) -> BeautifulSoup:
        try:
            response = self.session.get(url, headers=ScraperConfig.HEADERS)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to fetch data: Status code {response.status_code}"
                )
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {str(e)}")

    def scrape_jobs(
        self, keywords: str, location: str, max_jobs: int = 100
    ) -> List[JobData]:
        all_jobs = []
        start = 0

        while len(all_jobs) < max_jobs:
            try:
              #  url = self._build_search_url(keywords, location, start)
                url = self._build_search_url(
                    keywords=keywords,
                    location=location,
                    start=start,
                    f_AL=True,
                    f_E=[3, 4],
                    f_JT=["F", "C"],
                    f_WT=2,
                    f_JIYN=True,
                    f_TPR="r604800"
                )
                #print(url)
                soup = self._fetch_job_page(url)
                job_cards = soup.find_all("div", class_="base-card")

                if not job_cards:
                    break
                for card in job_cards:
                    job_data = self._extract_job_data(card)
                    if job_data:
                        all_jobs.append(job_data)
                        if len(all_jobs) >= max_jobs:
                            break
                print(f"Scraped {len(all_jobs)} jobs...")
                start += ScraperConfig.JOBS_PER_PAGE
                time.sleep(
                    random.uniform(ScraperConfig.MIN_DELAY, ScraperConfig.MAX_DELAY)
                )
            except Exception as e:
                print(f"Scraping error: {str(e)}")
                break
        return all_jobs[:max_jobs]

    def save_results(
        self, jobs: List[JobData], filename: str = "linkedin_jobs.json"
    ) -> None:
        if not jobs:
            return
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([vars(job) for job in jobs], f, indent=2, ensure_ascii=False)
        print(f"Saved {len(jobs)} jobs to {filename}")

        for job in jobs:
            data={
                "job_id": job.job_id,
                "company_name": job.company_name,
                "location": job.location,
                "job_title": job.job_title,
                "job_link": job.job_link,
                "job_description": job.job_description,
                "job_criteria": job.job_criteria,
                "job_posted_date": job.job_posted_date
            }
            dbutils.insert_job_posting(data)


def main():
    params = {"keywords": "Generative AI", "location": "united states", "max_jobs": 1000}

    scraper = LinkedInJobsScraper()
    jobs = scraper.scrape_jobs(**params)    
    scraper.save_results(jobs)


if __name__ == "__main__":
    main()


# [
#   "Finland",
#   "Switzerland",
#   "Denmark",
#   "Iceland",
#   "Norway",
#   "Sweden",
#   "Netherlands",
#   "Luxembourg",
#   "Ireland",
#   "Austria",
#   "Germany",
#   "New Zealand",
#   "Canada",
#   "Australia",
#   "Singapore",
#   "Hong Kong SAR",
#   "United Arab Emirates",
#   "United Kingdom",
#   "United States",
#   "Italy",
#   "Belgium",
#   "Malta",
#   "Liechtenstein",
#   "Japan"
# ]
