from fileModifier import FileModifierFactory, Filter
import json

fileJson = open("storage/json/data-fromat.json")
jsonData = json.load(fileJson)

modifiedRows = jsonData["sheets"][0]["modified_rows"]
filterData = Filter.parseFromJson(jsonData=jsonData["sheets"][0]["filter"])

modifier = FileModifierFactory.createModifier("csv","storage/csv/file1.csv", filterData, modifiedRows)
result = modifier.modify()

print(result)