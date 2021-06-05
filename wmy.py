from wmyblog import *

latest = today() - datetime.timedelta(days=4)
updateDaily(latest)
