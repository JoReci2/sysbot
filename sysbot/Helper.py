import pytz, datetime

class Helper():

    def convert_timezone_to_offset(self, timezone):
        """
        Converts the provided timezone to an offset.
        """
        try:
            tz = pytz.timezone(timezone)
            dt = datetime.datetime.now(tz)
            offset = dt.strftime("%z")
            formatted_offset = offset[:3] + ':' + offset[3:]
            return formatted_offset
        except pytz.UnknownTimeZoneError as e:
            raise pytz.UnknownTimeZoneError(f"Unknown timezone: {timezone}")
        except Exception as e:
            raise Exception(f"Failed to convert timezone to offset: {str(e)}")