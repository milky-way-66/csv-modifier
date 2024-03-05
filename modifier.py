import csv


class FileModifier:
    def modify(self):
        pass


class FileModifierFactory:
    @staticmethod
    def createModifier(fileType) -> FileModifier:
        match fileType:
            case 'csv':
                return CsvModifier()
            case _:
                raise Exception("file type are not supported")


class Range:
    def __init__(self, start, end) -> None:
        self.start = start
        self.end = end

    @staticmethod
    def parseFromDict(data: dict):
        return Range(data["start"], data["end"])

    def isBetween(self, value):
        return self.start <= value and value <= self.end

    def __str__(self) -> str:
        return f"start: {self.start} - end: {self.end}"


class CsvModifier(FileModifier):

    class TimeRange(Range):
        def isBetween(self, rangeTimeInSec: Range):
            startInSec = self.minToSec(self.start)
            endInSec = self.minToSec(self.end)

            return startInSec <= rangeTimeInSec.start and rangeTimeInSec.end <= endInSec

        def minToSec(min):
            return min * 60

    class Filter(FileModifier.Filter):
        def __init__(self, title: str, minutes: list, ids: list) -> None:
            self.title = title
            self.minutes = list(
                map(CsvModifier.TimeRange.parseFromDict, minutes))
            self.ids = list(map(Range.parseFromDict, ids))

        @staticmethod
        def parseFromJson(jsonData: dict):
            return CsvModifier.Filter(
                title=jsonData["title"],
                minutes=jsonData["minutes"],
                ids=jsonData["ids"])

        def checkValid(self, id, timeRange):
            return self.includeInIds(id) or self.includeInMinutes(timeRange)

        def includeInIds(self, id: int):
            return self.includeIn(self.ids, id)

        def includeInMinutes(self, rangeInSec: Range):
            return self.includeIn(self.minutes, rangeInSec)

        def includeIn(iter, value):
            for range in iter:
                if range.include(value=value):
                    return True
            return False

        def __str__(self) -> str:
            return f"title:{self.title}"

    def __init__(self, filePath: str, filter: Filter) -> None:
        self.filePath = filePath
        self.filter = filter

    ID_ROW_INDEX    = 0
    FROM_ROW_INDEX  = 1
    TO_ROW_INDEX    = 2

    def modify(self):

        with open(self.filePath, newline='') as csvFile:
            reader = csv.reader(csvFile, delimiter=',')

            for row in reader:
                rowId = row[self.ID_ROW_INDEX]
                rowTimeRange = Range(start=row[self.FROM_ROW_INDEX], end=row[self.TO_ROW_INDEX])

                if not self.filter.checkValid(rowId, rowTimeRange):
                   continue

                   
