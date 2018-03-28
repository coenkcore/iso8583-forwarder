from multi.BogorKota.padl.query import Reversal as BaseRev


class Reversal(BaseRev):
    def get_iso_payment(self):
        q = self.DBSession.query(self.iso_models.IsoPayment).filter_by(
                sspd_id=self.payment.id)
        return q.first()
