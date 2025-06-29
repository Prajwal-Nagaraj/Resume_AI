import csv
from jobspy import scrape_jobs
from datetime import datetime, timedelta

class SpeedyApplyTool:
    """A tool to find job listings and save them to a CSV file."""

    def find_and_save_jobs(self, search_term: str, location: str, time_days: int = 4, proxy_url: str = None) -> str | None:
        """Scrapes job listings for a given search term and location, 
        saves them to a CSV file prefixed with the current date, and returns the filename.

        Args:
            search_term: The job title or keywords to search for.
            location: The location to search for jobs in.
            time_days: Number of days old the jobs should be (default: 4 days).
            proxy_url: Optional proxy URL to use instead of the default proxy list.

        Returns:
            The filename of the saved CSV if successful, otherwise None.
        """
        # Calculate the date based on the time_days parameter
        date_ago = datetime.now() - timedelta(days=time_days)
        formatted_date = date_ago.strftime("%d %b %Y")

        google_search_query = f"{search_term} jobs near {location} since {formatted_date}"

        try:
            # Use provided proxy or fall back to proxy list
            proxies_to_use = [proxy_url] if proxy_url else None
            
            jobs_df = scrape_jobs(
                site_name=["linkedin"],
                search_term=search_term,
                google_search_term=google_search_query,
                location=location,
                results_wanted=20,
                hours_old=time_days * 24,  # Convert days to hours
                linkedin_fetch_description=True,
                proxies=proxies_to_use
            )
        except Exception as e:
            print(f"Error during job scraping: {e}")
            return None
        
        if jobs_df is not None and not jobs_df.empty:
            current_date_prefix = datetime.now().strftime("%Y-%m-%d")
            filename = f"{current_date_prefix}_{search_term.replace(' ', '_')}_jobs.csv"
            try:
                jobs_df.to_csv(filename, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
                print(f"Found {len(jobs_df)} jobs. Saved to {filename}")
                return filename
            except Exception as e:
                print(f"Error saving jobs to CSV: {e}")
                return None
        else:
            print("No jobs found or an error occurred during scraping.")
            return None

if __name__ == "__main__":
    # Example usage of the SpeedyApplyTool:
    tool = SpeedyApplyTool()
    
    search_query = "AI Product Manager"
    job_location = "New York, USA"
    time_days = 7  # Search for jobs posted in the last 7 days
    
    saved_filename = tool.find_and_save_jobs(search_term=search_query, location=job_location, time_days=time_days, proxy_url="https://spm7e96ly4:Pl=r66vUAut2asdwE0@gate.decodo.com:10001")
    
    if saved_filename:
        print(f"Process completed. Job data saved to: {saved_filename}")
    else:
        print("Process completed. No job data was saved.")