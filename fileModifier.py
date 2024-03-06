import csv

class FileModifier:
    def modify(self):
        pass

class FileModifierFactory:
    @staticmethod
    def createModifier(fileType, *args) -> FileModifier:
        match fileType:
            case 'csv':
                return CsvModifier(*args)
            case _:
                raise Exception("file type are not supported")

class Range:
    
    @staticmethod
    def parseFromDict(data: dict):
        return Range( int(data["start"]), int(data["end"]))

    def __init__(self, start:int, end:int) -> None:
        self.start = start
        self.end = end

    def contain(self, value):
        return self.start <= value and value <= self.end

    def __str__(self) -> str:
        return f"start: {self.start} - end: {self.end}"

class TimeRange(Range):
        
        @staticmethod
        def parseFromDict(data: dict):
            return TimeRange( int(data["start"]), int(data["end"]))

        def contain(self, rangeTimeInSec: Range):
            startInSec = self.minToSec(self.start)
            endInSec = self.minToSec(self.end)

            return startInSec <= rangeTimeInSec.start and rangeTimeInSec.end <= endInSec

        @staticmethod
        def minToSec(min):
            return min * 60


class Filter():

    @staticmethod
    def parseFromJson(jsonData: dict):
        return Filter(
            minutes=jsonData["minutes"],
            ids=jsonData["ids"])

    def __init__(self, minutes: list, ids: list):
        self.minutes = list(
            map(TimeRange.parseFromDict, minutes))
        self.ids = list(map(Range.parseFromDict, ids))

    def isValid(self, id, timeRange) -> bool:
        return self.includeInIds(id) or self.includeInMinutes(timeRange)

    def includeInIds(self, id: int) -> bool:
        return self.includeIn(self.ids, id)

    def includeInMinutes(self, rangeInSec: Range) -> bool:
        return self.includeIn(self.minutes, rangeInSec)

    def includeIn(self,iter, value) -> bool:
        for range in iter:
            if range.contain(value):
                return True
        return False
        

class ModifiedRow():

    @staticmethod
    def parseFromDict(row:dict):
        return ModifiedRow(row["id"], row["content"])

    def __init__(self, id:int, content:str):
        self.id = id
        self.content = content

class CsvModifier(FileModifier):

    fileData = None

    def __init__(self, filePath: str, filter: Filter, modifiedRows:list):
        self.filePath = filePath
        self.filter = filter
        self.modifiedRows = list(map(ModifiedRow.parseFromDict, modifiedRows))

    def modify(self) -> list:
        with open(self.filePath, newline='') as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',')
            
            #skip header line of csv file
            next(csvReader)
            self.modifyRows(csvReader)
        
        self.saveModifiedFile()
        return self.filterRows()

    ROW_ID_INDEX = 0
    ROW_START_INDEX = 1
    ROW_END_INDEX = 2
    ROW_CONTENT_INDEX = 3
    def modifyRows(self, rows) -> None:
        result = []
        for row in rows:
            modifiedRow = self.getModifiedRow(row=row)
            if modifiedRow is not None:
                row[self.ROW_CONTENT_INDEX] = modifiedRow.content 
            result.append(row)
            
        self.fileData = result
        
    def getModifiedRow(self, row) -> ModifiedRow|None:
        rowId = int(row[self.ROW_ID_INDEX])
        
        for modifiedRow in self.modifiedRows:
            if rowId == modifiedRow.id:
                return modifiedRow
            
        return None

    def filterRows(self) -> list:
        result = []
        for row in self.fileData:
            rowId = int(row[self.ROW_ID_INDEX])
            rowTimeRange = Range(
                start=int(row[self.ROW_START_INDEX]), end=int(row[self.ROW_END_INDEX]))

            if self.filter.isValid(rowId, rowTimeRange):
                result.append(row)

        return result
    
    def saveModifiedFile(self):
        pass
