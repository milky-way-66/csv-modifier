from modifier import CsvModifier
import json

fileJson = open("form-data.json")
jsonData = json.load(fileJson)

filterData = CsvModifier.Filter.parseFromJson(jsonData=jsonData["sheet_filter"][0])

modifier = CsvModifier("./csv/file1.csv", filterData)
modifier.modify()