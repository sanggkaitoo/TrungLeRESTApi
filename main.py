from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from os.path import exists
import json

app = FastAPI()

templates = Jinja2Templates(directory="html-template")


@app.get("/first-post-template", response_class=HTMLResponse)
def first_post(request: Request):
    return templates.TemplateResponse("form-api.html", {"request": request})


@app.post("/first-post")
async def append_or_insert(file: UploadFile = File(...)):
    contents = await file.read()
    data_submit = json.loads(contents.decode("utf-8"))

    if not exists("data.txt"):
        with open("data.txt", 'w') as db:
            content_write = json.dumps(data_submit)
            db.write(content_write)
            return {"status": "inserted"}
    else:
        with open("data.txt", 'r') as db:
            data_in_file = json.loads(db.read())
        check = 0
        if isinstance(data_in_file, list):
            for data in data_in_file:
                if data_submit["poolId"] == data["poolId"]:
                    data["poolValues"].extend(data_submit["poolValues"])
                    check = 1
            if check == 0:
                data_in_file.append(data_submit)
            data_save = data_in_file
        else:
            if data_submit["poolId"] == data_in_file["poolId"]:
                data_in_file["poolValues"].extend(data_submit["poolValues"])
                data_save = data_in_file
                check = 1
            else:
                data_save = [data_in_file, data_submit]

        with open("data.txt", 'w') as db:
            db.write(json.dumps(data_save))

    context = "appended" if check == 1 else "inserted"

    return {context}


@app.post("/second-post")
async def calculate_quantile(file: UploadFile = File(...)):
    contents = await file.read()
    data_submit = json.loads(contents.decode("utf-8"))

    with open("data.txt", 'r') as db:
        data_in_file = json.loads(db.read())
    check = 0
    if isinstance(data_in_file, list):
        for data in data_in_file:
            if data_submit["poolId"] == data["poolId"]:
                result = calculator_quantile(data_submit, data)
                check = 1
                break
    else:
        if data_submit["poolId"] == data_in_file["poolId"]:
            result = calculator_quantile(data_submit, data_in_file)
            check = 1

    print(result)
    print(check)

    context = {
        "quantile": result[0],
        "length": result[1],
        "check": check
    }

    return {
        "quantile": result[0],
        "length": result[1],
    }


def calculator_quantile(submit_dict, data_dict):
    num_arr = data_dict["poolValues"]
    num_arr.sort()
    pool_len = len(num_arr)
    percentile = submit_dict["percentile"] / 100
    quantile = percentile * (pool_len + 1)

    return [quantile, pool_len]
