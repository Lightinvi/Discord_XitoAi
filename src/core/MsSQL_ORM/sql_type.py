#pylint:disable = R0903
"""SQL相關資料型態與轉換"""
class _Exact():
    @staticmethod
    def bit() -> str:
        """bit資料型態,其值有 1、0 或 NULL 幾種
        字串值 TRUE 和 FALSE 可以轉換成 bit 值:TRUE 會轉換成 1,FALSE 則轉換成 0.
        轉換成位元會將任何非零的值升級成 1.

        Returns:
            str: 轉換字串
        """
        return "bit"

    @staticmethod
    def bigint() -> str:
        """bigint資料型態,範圍為正負2^64的整數型態

        Returns:
            str: 轉換字串
        """
        return "bigint"

    @staticmethod
    def decimal(length:tuple[int]=(18, 0)) -> str:
        """decimal資料型態,固定有效位數和小數位數的數字.
        資料型態大小設定中 tuple 左側為設定有效位數:右側為設定小數位數\n
        (有效位數)
        要儲存的最大小數位數總數。 此數目包括小數點的左右兩側。 有效位數必須是從 1 到最大有效位數 38 的值。 預設有效位數是 18。\n
        (小數位數)
        小數點右側所能儲存的小數位數。 這個數字會從 p 中減去，以判斷小數點左邊的最大位數。
        小數位數必須是介於 0 到 p 間的值，且只能在已指定有效位數時指定。
        預設小數位數是 0,因此 0 <= s<= p。 最大儲存體大小會隨著有效位數而不同。

        Args:
            length (tuple[int], optional): 資料型態大小. Defaults to (10, 2).

        Raises:
            TypeError: 'length' 資料型態不等於 'int'

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, tuple) or not isinstance(length, int):
            raise TypeError
        if isinstance(length, int):
            length = (length, 0)
        elif not length:
            length = (18, 0)

        return F"decimal({length[0], length[1]})"

    @staticmethod
    def int_() -> str:
        """int資料型態,範圍為正負2^32的整數型態

        Returns:
            str: 轉換字串
        """
        return "int"

    @staticmethod
    def money() -> str:
        """money資料型態,其精確度可達它們所代表之金融單位的萬分之一。
        針對 money 和 smallmoney 資料類型的精確度可達它們所代表之金融單位的百分之一。\n
        詳閱:https://learn.microsoft.com/zh-tw/sql/t-sql/data-types/money-and-smallmoney-transact-sql?view=sql-server-ver16

        Returns:
            str: 轉換字串
        """
        return "money"

    @staticmethod
    def numeric(length:tuple[int] = (18, 0)) -> str:
        """numeric資料型態,固定有效位數和小數位數的數字.
        資料型態大小設定中 tuple 左側為設定有效位數:右側為設定小數位數\n
        (有效位數)
        要儲存的最大小數位數總數。 此數目包括小數點的左右兩側。 有效位數必須是從 1 到最大有效位數 38 的值。 預設有效位數是 18。\n
        (小數位數)
        小數點右側所能儲存的小數位數。 這個數字會從 p 中減去，以判斷小數點左邊的最大位數。
        小數位數必須是介於 0 到 p 間的值，且只能在已指定有效位數時指定。
        預設小數位數是 0,因此 0 <= s<= p。 最大儲存體大小會隨著有效位數而不同。

        Args:
            length (tuple[int], optional): 資料型態大小. Defaults to (10, 2).

        Raises:
            TypeError: 'length' 資料型態不等於 'int'

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, tuple) or not isinstance(length, int):
            raise TypeError
        if isinstance(length, int):
            length = (length, 0)
        elif length:
            length = (18, 0)

        return F"numeric({length[0], length[1]})"

    @staticmethod
    def smallint() -> str:
        """smallint資料型態,範圍為正負2^16的整數型態

        Returns:
            str: 轉換字串
        """
        return "smallint"

    @staticmethod
    def smallmoney() -> str:
        """smallmoney資料型態,其精確度可達它們所代表之金融單位的萬分之一。
        針對 money 和 smallmoney 資料類型的精確度可達它們所代表之金融單位的百分之一。\n
        詳閱:https://learn.microsoft.com/zh-tw/sql/t-sql/data-types/money-and-smallmoney-transact-sql?view=sql-server-ver16

        Returns:
            str: 轉換字串
        """
        return "smallmoney"

    @staticmethod
    def tinyint() -> str:
        """tinyint資料型態,範圍為 -2^1 ~ +2^8-1 的整數型態

        Returns:
            str: 轉換字串
        """
        return "tinyint"

class _Approximate():
    @staticmethod
    def float_(length:int=53) -> str:
        """float資料型態,用來搭配浮點數值資料使用的近似數值資料類型。 浮點數資料是近似的；因此，並非資料類型範圍內的所有值都能夠精確地表示。

        Args:
            length (int, optional): 資料型態大小. Defaults to 53.

        Raises:
            ValueError: 超出資料型態範圍(25 <= length <= 53)

        Returns:
            str: 轉換字串
        """
        if not 25 <= length <= 53:
            raise ValueError

        return F"float({length})"

    @staticmethod
    def real(length:int=24) -> str:
        """real資料型態,,用來搭配浮點數值資料使用的近似數值資料類型。 浮點數資料是近似的；因此，並非資料類型範圍內的所有值都能夠精確地表示。

        Args:
            length (int, optional): 資料型態大小. Defaults to 24.

        Raises:
            ValueError: 超出資料型態範圍(1 <= length <= 24)

        Returns:
            str: 轉換字串
        """
        if not 1 <= length <= 24:
            raise ValueError

        return F"real({length})"

class _DateAndTime():
    @staticmethod
    def date() -> str:
        """date資料型態,儲存yyyy-MM-dd格式

        Returns:
            str: 轉換字串
        """
        return "date"

    @staticmethod
    def datetime() -> str:
        """datetime資料型態,YYYY-MM-DD hh:mm:ss.nnn格式

        YYYY 是代表年份的四位數，範圍介於 1753 至 9999 之間。

        MM 是代表指定年份中某個月份的兩位數，範圍介於 01 至 12 之間。

        DD 是代表指定月份中某個日期的兩位數，範圍介於 01 至 31 之間 (視月份而定)。

        hh 是代表小時的兩位數，範圍介於 00 至 23 之間。

        mm 是代表分鐘的兩位數，範圍介於 00 至 59 之間。

        ss 是代表秒鐘的兩位數，範圍介於 00 至 59 之間。

        n* 是代表小數秒數的零至三位數，範圍介於 0 至 999 之間。

        Returns:
            str: 轉換字串
        """
        return "datetime"

    @staticmethod
    def datetime2(length:int = 7) -> str:
        """datetime2資料型態,YYYY-MM-DD hh:mm:ss.nnnnnnn格式

        YYYY 是代表年份的四位數字，範圍介於 0001 至 9999 之間。

        MM 是代表指定年份中某個月份的兩位數字，範圍介於 01 至 12 之間。

        DD 是代表指定月份中某個日期的兩位數字，範圍介於 01 至 31 之間 (視月份而定)。

        hh 是代表小時的兩位數字，範圍介於 00 至 23 之間。

        mm 是代表分鐘的兩位數字，範圍介於 00 至 59 之間。

        ss 是代表秒鐘的兩位數字，範圍介於 00 至 59 之間。

        n* 是代表小數秒數的零至七位數字，範圍介於 0 至 9999999 之間。 在  中，毫秒會在 n > 3 時遭到截斷。

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, int):
            raise TypeError
        if not 0 <= length <= 7:
            raise ValueError
        return F"datetime2({length})"

    @staticmethod
    def datetimeoffset(length:int=7) -> str:
        """datetimeoffset資料型態,儲存yyyy-MM-dd hh:mm:ss.nnnnnnn格式

        YYYY 是代表年份的四位數，範圍介於 0001 至 9999 之間。

        MM 是代表指定年份中某個月份的兩位數，範圍介於 01 至 12 之間。

        DD 是代表指定月份中某個日期的兩位數，範圍介於 01 至 31 之間 (視月份而定)。

        hh 是代表小時的兩位數，範圍介於 00 至 23 之間。

        mm 是代表分鐘的兩位數，範圍介於 00 至 59 之間。

        ss 是代表秒鐘的兩位數，範圍介於 00 至 59 之間。

        n* 是代表小數秒數的零至七位數，範圍介於 0 至 9999999 之間。

        hh 是兩位數，範圍介於 -14 至 +14 之間。

        mm 是兩位數，範圍介於 00 至 59 之間。

        Args:
            length (int, optional): 有效小數點範圍. Defaults to 7.

        Raises:
            TypeError: 'length' 資料型態不等於 'int'
            ValueError: 超出有效小數點範圍 (0 <= length <= 7)

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, int):
            raise TypeError
        if not 0 <= length <= 7:
            raise ValueError
        return F"datetimeoffset({length})"

    @staticmethod
    def smalldatetime() -> str:
        """smalldatetime資料型態,儲存YYYY-MM-DD hh:mm:ss格式

        YYYY 是代表年份的四位數，範圍介於 1900 至 2079 之間。

        MM 是代表指定年份中某個月份的兩位數，範圍介於 01 至 12 之間。

        DD 是代表指定月份中某個日期的兩位數，範圍介於 01 至 31 之間 (視月份而定)。

        hh 是代表小時的兩位數，範圍介於 00 至 23 之間。

        mm 是代表分鐘的兩位數，範圍介於 00 至 59 之間。

        ss 是代表秒鐘的兩位數，範圍介於 00 至 59 之間。 29.998 秒或以下值會無條件捨去到最接近的分鐘。 29.999 秒或以上值會無條件進位到最接近的分鐘。

        Returns:
            str: 轉換字串
        """
        return "smalldatetime"

    @staticmethod
    def time(length:int=7) -> str:
        """time資料型態,儲存hh:mm:ss.nnnnnnn hh:mm:ss格式

        Args:
            length (int, optional): 有效小數點範圍. Defaults to 7.

        Raises:
            TypeError: 'length' 資料型態不等於 'int'
            ValueError: 超出有效小數點範圍 (0 <= length <= 7)

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, int):
            raise TypeError
        if not 0 <= length <= 7:
            raise ValueError

        return F"time({length})"

class _Character():
    @staticmethod
    def char(length:int=30) -> str:
        """char資料型態,固定大小字串資料。

        Args:
            length (int, optional): 資料型態大小. Defaults to 30.

        Raises:
            TypeError: 'length' 資料型態不等於 'int'
            ValueError: ValueError: 超出有效儲存大小範圍 (1 <= length <= 8000)

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, int):
            raise TypeError

        if not 1 <= length <= 8000:
            raise ValueError

        return F"char({length})"

    @staticmethod
    def varchar(length:int=30) -> str:
        """char資料型態,可變大小字串資料。

        Args:
            column (str): 欄位名稱
            length (int, optional): 資料型態大小. Defaults to 30.
            join_mode (bool, optional): 使用join表格鍵入時需改成True. Defaults to False.

        Raises:
            TypeError: 'length' 資料型態不等於 'int'
            ValueError: ValueError: 超出有效儲存大小範圍 (1 <= length <= 8000)

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, int):
            raise TypeError

        if length == -1:
            length = 'max'
        elif not 1 <= length <= 8000:
            raise ValueError

        return F"varchar({length})"

class _UnicodeCharacter():

    @staticmethod
    def nchar(length:int=30) -> str:
        """nchar資料型態,固定大小Unicode字串資料。

        Args:
            length (int, optional): 資料型態大小. Defaults to 30.

        Raises:
            TypeError: 'length' 資料型態不等於 'int'
            ValueError: ValueError: 超出有效儲存大小範圍 (1 <= length <= 4000)

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, int):
            raise TypeError

        if not 1 <= length <= 4000:
            raise ValueError

        return F"nchar({length})"

    @staticmethod
    def nvarchar(length:int=30) -> str:
        """nchar資料型態,可變大小Unicode字串資料。

        Args:
            length (int, optional): 資料型態大小. Defaults to 30.

        Raises:
            TypeError: 'length' 資料型態不等於 'int'
            ValueError: ValueError: 超出有效儲存大小範圍 (1 <= length <= 4000)

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, int):
            raise TypeError

        if length == -1:
            length = 'max'
        elif not 1 <= length <= 4000:
            raise ValueError

        return F"nvarchar({length})"

class _Binary():
    @staticmethod
    def binary(length:int=30) -> str:
        """binary資料型態,固定長度的二進位資料.

        Args:
            length (int, optional): 資料型態大小. Defaults to 30.

        Raises:
            TypeError: 'length' 資料型態不等於 'int'
            ValueError: 超出資料型態範圍(1 <= length <= 8000)

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, int):
            raise TypeError("length 需要是 'int'")

        if not 1 <= length <= 8000:
            raise ValueError('超出資料型態範圍')

        return F"binary({length})"

    @staticmethod
    def varbinary(length:int=30) -> str:
        """binary資料型態,可變長度的二進位資料.

        Args:
            length (int, optional): 資料型態大小. Defaults to 30.

        Raises:
            TypeError: 'length' 資料型態不等於 'int'
            ValueError: 超出資料型態範圍(1 <= length <= 8000)

        Returns:
            str: 轉換字串
        """
        if not isinstance(length, int):
            raise TypeError

        if length == -1:
            length = 'max'
        elif not 1 <= length <= 8000:
            raise ValueError

        return F"varbinary({length})"

class SQLType():
    """SQL資料型態"""

    exact = _Exact
    """精確數值"""

    approximate = _Approximate
    """近似數值"""

    datetime = _DateAndTime
    """日期和時間"""

    character = _Character
    """字元字串"""

    unicode = _UnicodeCharacter
    """Unicode字元字串"""

    binary = _Binary
    """二進制字串"""
