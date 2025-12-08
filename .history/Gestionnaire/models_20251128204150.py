class Gestionnaire(SafeDeleteModel,LifecycleModel):
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'gestionnaire'})

    def __str__(self):
        return self.user.username