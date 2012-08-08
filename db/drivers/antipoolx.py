import antipool

from db.drivers import Driver


class AntipoolDriver(Driver):

    def __init__(self, driver, **kwargs):
        super(AntipoolDriver, self).__init__(*[driver], **kwargs)
        self.pool = antipool.ConnectionPool(driver, **kwargs)
        antipool.initpool(self.pool)

    def connect(self):
        return self.pool.connection()


register = AntipoolDriver.register
