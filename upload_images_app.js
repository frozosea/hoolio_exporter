const fetch = require('cross-fetch');
const FormData = require('form-data');
const fs = require('fs');
const express = require('express')
const app = express()
app.use(express.json())
const port = 3000

app.get('/', (req, res) => {
    res.json({"health": "ok"})
})
app.post('/upload', async (req, res) => {
    const uploadPhotos = async (filepath, ip) => {
        let form = new FormData()
        form.append('Files[]', fs.createReadStream(filepath));
        form.append("Func", "UploadPhotos")
        form.append("UploadedFiles", "1")
        if(ip){
            form.append("IP", ip)
        }
        form.append("SiteID", 4);
        const response = await fetch("https://static.my.ge/", {
            "method": "POST",
            "headers": {
                "accept": "*/*",
                "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5,zh;q=0.4",
                // "content-type": "multipart/form-data; boundary=----WebKitFormBoundarylTIWgG0A01whGkk3",
                "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "Referer": "https://www.myhome.ge/ru/my/addProduct/2324281",
                "Referrer-Policy": "unsafe-url"
            },
            "body": form
        });
        return await response.json()
    }
    const body = req.body
    if (body.filepath) {
        const response = await uploadPhotos(body.filepath, body.ip)
        if (response.Data) {
            if (response.Data.FilesList) {
                res.json({"url": response.Data.FilesList[0]})
                return
            }
        }
    }
    res.json({"success": false, "error": "no data"})
})
app.listen(port, () => {
    console.log(`Upload images to myhome app listening on port ${port}`)
})