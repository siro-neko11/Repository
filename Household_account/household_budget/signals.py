# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import BalanceOfPayments, Saving
# from django.db import transaction

# @receiver(post_save, sender=BalanceOfPayments)
# def create_saving_entry(sender, instance, created, **kwargs):
#     """
#     収支データが保存されたときに、対応するSavingデータを作成するシグナル
#     """
#     if created:
#         # トランザクションを使用して原子的な操作を行う
#         with transaction.atomic():
#             # Savingデータを作成
#             year_month_str = instance.event_date.strftime("%Y-%m") if instance.event_date else None
#             Saving.objects.create(
#                 saving=instance,
#                 amount=instance.saving,  # ここで保存するデータを適切に選択する
#                 year_month=year_month_str
#             )
