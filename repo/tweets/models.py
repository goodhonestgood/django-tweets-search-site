from django.db import models
from django.contrib.auth import get_user_model


# from django.core.exceptions import ValidationError

class SubscribeTwitter(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, blank=True, null=True,
                             related_name='create')
    tw_username = models.CharField(max_length=20, )
    tw_id = models.CharField(max_length=20, )

    def __str__(self):
        return "{} : {} : {}".format(self.user, self.tw_username, self.tw_id)
