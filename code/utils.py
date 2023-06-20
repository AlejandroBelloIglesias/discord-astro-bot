import requests
import keys
import json
import time
import asyncio

def isImage(attachment):
    return attachment.content_type.startswith('image')


def upload_submission(image_url):
    session_key = keys.getSessionKey()
    # Define the request payload
    payload = {
        "request-json": json.dumps({
        "session": session_key,
        "url": image_url,
        })
    }
    # Make the POST request
    response = requests.post('http://nova.astrometry.net/api/url_upload', data=payload)
    return response.json()['subid']


def getUserImageFromSubId(subid):
    submission_response = submission_status(subid)
    return submission_response['user_images'][0]


def submission_status(subid):
    url = f"http://nova.astrometry.net/api/submissions/{subid}"
    response = requests.post(url)
    return response.json()


async def polling_job(subid, ctx, success_handler, failure_handler, timeout_handler):
    # Polling loop
    timeout: float = time.time() + 600  # Set max timeout to 10 minutes (600 sec)
    while True:
        await asyncio.sleep(5)

        if not has_job(subid):
            continue

        response = submission_status(subid)
        job_id: int = response['jobs'][0]
        job_status: str = jobStatus(job_id)
        #TODO: Start job tracking in a separate function.

        if job_status == 'success':
            result_url = f"http://nova.astrometry.net/annotated_display/{job_id}"
            await success_handler(ctx=ctx, result_url=result_url, subid=subid)
            break

        if job_status == 'failure':
            await failure_handler(ctx=ctx, subid=subid)
            break

        if time.time() > timeout:
            await timeout_handler(ctx=ctx)
            break


def jobStatus(job_id: int):
    url: str = f"https://nova.astrometry.net/api/jobs/{job_id}"
    response = requests.post(url)
    return response.json()['status']


def has_job(subid):
    poll_response = submission_status(subid)
    jobs = poll_response['jobs']
    return len(jobs) > 0 and jobs[0] is not None  #Might return [None] lol
