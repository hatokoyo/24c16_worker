from django.db import models


class Koban(models.Model):
    name = models.TextField(primary_key=True)  # Field name made lowercase.
    koban1 = models.TextField(blank=True, null=True)
    koban2 = models.TextField(blank=True, null=True)
    koban3 = models.TextField(blank=True, null=True)
    koban4 = models.TextField(blank=True, null=True)
    koban5 = models.TextField(blank=True, null=True)
    koban6 = models.TextField(blank=True, null=True)
    koban7 = models.TextField(blank=True, null=True)
    koban8 = models.TextField(blank=True, null=True)
    koban9 = models.TextField(blank=True, null=True)
    koban10 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'koban'




class nippo(models.Model):
    idx = models.CharField(primary_key=True,max_length=10)
    userid = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    start = models.TextField(blank=True, null=True)
    end = models.TextField(blank=True, null=True)
    zangyo = models.TextField(blank=True, null=True)
    total_time = models.TextField(blank=True, null=True)
    total_break = models.TextField(blank=True, null=True)
    koban = models.TextField(blank=True, null=True)
    add_time=models.TextField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    break_start = models.TextField(blank=True, null=True)
    break_end = models.TextField(blank=True, null=True)
    trans = models.IntegerField(blank=True, null=True)
    trans_office = models.TextField(blank=True, null=True)
    sequence = models.IntegerField(blank=True, null=True)
    total_kinmu = models.TextField(blank=True, null=True)
    lunch = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'nippo'



