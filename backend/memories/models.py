from django.db import models
from django.utils import timezone


class Person(models.Model):
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('U', '未知'),
    ]
    STATUS_CHOICES = [
        ('confirmed', '已确认'),
        ('pending', '待确认'),
        ('conflicted', '信息冲突'),
    ]

    name = models.CharField('姓名', max_length=100)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES, default='U')
    birth_year = models.IntegerField('出生年份', null=True, blank=True)
    death_year = models.IntegerField('逝世年份', null=True, blank=True)
    birth_place = models.CharField('出生地', max_length=200, blank=True)
    description = models.TextField('人物简介', blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    status = models.CharField('确认状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.CharField('创建人', max_length=50, default='家属')

    class Meta:
        db_table = 'person'
        ordering = ['birth_year', 'name']

    def __str__(self):
        return self.name


class Alias(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='aliases', verbose_name='所属人物')
    alias_name = models.CharField('别名/昵称', max_length=100)
    usage_context = models.CharField('使用场景', max_length=200, blank=True, help_text='如：乳名、旧时称呼、工作用名等')
    added_by = models.CharField('补注人', max_length=50, default='晚辈')
    created_at = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        db_table = 'alias'

    def __str__(self):
        return f'{self.person.name} - {self.alias_name}'


class MigrationInfo(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='migrations', verbose_name='所属人物')
    from_place = models.CharField('迁出地', max_length=200)
    to_place = models.CharField('迁入地', max_length=200)
    move_year = models.IntegerField('迁居年份', null=True, blank=True)
    reason = models.CharField('迁居原因', max_length=500, blank=True)
    added_by = models.CharField('补注人', max_length=50, default='晚辈')
    created_at = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        db_table = 'migration_info'
        ordering = ['move_year']

    def __str__(self):
        return f'{self.person.name} {self.move_year}年 {self.from_place}→{self.to_place}'


class Relationship(models.Model):
    RELATION_CHOICES = [
        ('father', '父亲'),
        ('mother', '母亲'),
        ('spouse', '配偶'),
        ('child', '子女'),
        ('sibling', '兄弟姐妹'),
        ('grandparent', '祖父母'),
        ('grandchild', '孙辈'),
        ('uncle_aunt', '叔伯/姑姨'),
        ('nephew_niece', '侄/甥'),
        ('cousin', '堂/表亲'),
        ('in_law', '姻亲'),
        ('other', '其他'),
    ]

    from_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='relationships_from', verbose_name='人物A')
    to_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='relationships_to', verbose_name='人物B')
    relation_type = models.CharField('关系类型', max_length=20, choices=RELATION_CHOICES)
    relation_note = models.CharField('关系备注', max_length=300, blank=True, help_text='详细说明，如：大舅、二伯母等')
    added_by = models.CharField('补注人', max_length=50, default='家属')
    created_at = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        db_table = 'relationship'

    def __str__(self):
        return f'{self.from_person.name} - {self.get_relation_type_display()} - {self.to_person.name}'


class Photo(models.Model):
    ERA_CHOICES = [
        ('1920s', '1920年代'),
        ('1930s', '1930年代'),
        ('1940s', '1940年代'),
        ('1950s', '1950年代'),
        ('1960s', '1960年代'),
        ('1970s', '1970年代'),
        ('1980s', '1980年代'),
        ('1990s', '1990年代'),
        ('2000s', '2000年代'),
        ('2010s', '2010年代'),
        ('2020s', '2020年代'),
        ('unknown', '年代不详'),
    ]
    SCENE_CHOICES = [
        ('family_portrait', '全家福'),
        ('wedding', '婚礼'),
        ('daily_life', '日常生活'),
        ('festival', '节庆聚会'),
        ('travel', '旅行出游'),
        ('work_school', '工作/求学'),
        ('childhood', '童年'),
        ('military', '军旅'),
        ('funeral', '丧葬/纪念'),
        ('other', '其他'),
    ]
    SOURCE_CHOICES = [
        ('old_album', '老相册'),
        ('family_donation', '家人捐赠'),
        ('scanned', '扫描翻拍'),
        ('digital_camera', '数码相机'),
        ('phone', '手机拍摄'),
        ('social_media', '社交媒体'),
        ('other', '其他来源'),
    ]
    STATUS_CHOICES = [
        ('archived', '已归档'),
        ('annotating', '补注中'),
        ('completed', '补注完成'),
    ]

    title = models.CharField('照片标题', max_length=200, blank=True)
    image = models.ImageField('照片文件', upload_to='photos/', blank=True, null=True)
    era = models.CharField('年代', max_length=20, choices=ERA_CHOICES, default='unknown')
    scene = models.CharField('场景', max_length=30, choices=SCENE_CHOICES, default='other')
    source = models.CharField('来源', max_length=30, choices=SOURCE_CHOICES, default='old_album')
    location = models.CharField('拍摄地点', max_length=300, blank=True)
    taken_year = models.IntegerField('拍摄年份', null=True, blank=True)
    description = models.TextField('事件背景描述', blank=True, help_text='老人口述的事件背景')
    status = models.CharField('补注状态', max_length=20, choices=STATUS_CHOICES, default='archived')
    uploader = models.CharField('上传人', max_length=50, default='家属')
    created_at = models.DateTimeField('上传时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'photo'
        ordering = ['-taken_year', '-created_at']

    def __str__(self):
        return self.title or f'照片-{self.id}'


class PersonInPhoto(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='people_in_photo', verbose_name='照片')
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos', verbose_name='关联人物')
    person_name_override = models.CharField('暂用名/待确认名', max_length=100, blank=True, help_text='人物未确认时填写')
    position_note = models.CharField('位置说明', max_length=200, blank=True, help_text='如：前排左一、后排中间等')
    old_title = models.CharField('当时称呼', max_length=100, blank=True, help_text='拍摄时的称呼，如：小妹、阿强等')
    role_note = models.CharField('角色/状态备注', max_length=300, blank=True)
    added_by = models.CharField('标注人', max_length=50, default='家属')
    created_at = models.DateTimeField('标注时间', auto_now_add=True)

    class Meta:
        db_table = 'person_in_photo'

    def __str__(self):
        name = self.person.name if self.person else self.person_name_override or '未命名'
        return f'{self.photo} - {name}'


class MemoryFragment(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '待整理'),
        ('published', '已沉淀'),
        ('conflicted', '内容冲突'),
    ]

    title = models.CharField('回忆标题', max_length=300)
    content = models.TextField('回忆内容')
    related_photos = models.ManyToManyField(Photo, blank=True, related_name='memories', verbose_name='关联照片')
    related_people = models.ManyToManyField(Person, blank=True, related_name='memories', verbose_name='关联人物')
    occur_year = models.IntegerField('发生年份', null=True, blank=True)
    occur_place = models.CharField('发生地点', max_length=300, blank=True)
    author = models.CharField('回忆讲述/撰写人', max_length=100, default='家属')
    status = models.CharField('整理状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'memory_fragment'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ConflictVersion(models.Model):
    FIELD_CHOICES = [
        ('person_name', '人物姓名'),
        ('person_relation', '亲属关系'),
        ('photo_date', '拍摄时间'),
        ('photo_location', '拍摄地点'),
        ('photo_people', '照片人物'),
        ('memory_content', '回忆内容'),
        ('other', '其他信息'),
    ]
    STATUS_CHOICES = [
        ('open', '待确认'),
        ('resolved', '已确认'),
        ('rejected', '已驳回'),
    ]

    related_person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name='conflicts', verbose_name='关联人物')
    related_photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True, related_name='conflicts', verbose_name='关联照片')
    related_memory = models.ForeignKey(MemoryFragment, on_delete=models.CASCADE, null=True, blank=True, related_name='conflicts', verbose_name='关联回忆')
    conflict_field = models.CharField('冲突字段', max_length=30, choices=FIELD_CHOICES, default='other')
    version_a = models.TextField('版本A（原版本）')
    version_a_author = models.CharField('版本A提交人', max_length=100, default='')
    version_b = models.TextField('版本B（新版本）')
    version_b_author = models.CharField('版本B提交人', max_length=100, default='')
    description = models.TextField('冲突说明', blank=True)
    status = models.CharField('处理状态', max_length=20, choices=STATUS_CHOICES, default='open')
    resolved_version = models.CharField('最终版本', max_length=1, choices=[('A', '版本A'), ('B', '版本B')], null=True, blank=True)
    resolved_by = models.CharField('确认人', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    resolved_at = models.DateTimeField('解决时间', null=True, blank=True)

    class Meta:
        db_table = 'conflict_version'
        ordering = ['-created_at']

    def __str__(self):
        target = self.related_person or self.related_photo or self.related_memory or '无关联'
        return f'冲突-{self.id}-{self.get_conflict_field_display()}-{target}'


class FamilyConfirmation(models.Model):
    CONFIRM_TYPE_CHOICES = [
        ('person', '人物信息'),
        ('relation', '亲属关系'),
        ('photo_info', '照片信息'),
        ('photo_person', '照片人物'),
        ('memory', '回忆内容'),
        ('conflict', '冲突版本'),
    ]
    STATUS_CHOICES = [
        ('pending', '待投票'),
        ('approved', '已通过'),
        ('rejected', '已否决'),
        ('tied', '平票待议'),
    ]

    confirm_type = models.CharField('确认类型', max_length=20, choices=CONFIRM_TYPE_CHOICES)
    related_person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name='confirmations')
    related_photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True, related_name='confirmations')
    related_memory = models.ForeignKey(MemoryFragment, on_delete=models.CASCADE, null=True, blank=True, related_name='confirmations')
    related_conflict = models.ForeignKey(ConflictVersion, on_delete=models.CASCADE, null=True, blank=True, related_name='confirmations')
    title = models.CharField('确认事项', max_length=300)
    detail = models.TextField('详细内容')
    proposer = models.CharField('提案人', max_length=100, default='家属')
    status = models.CharField('确认状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    vote_approve = models.IntegerField('赞成票', default=0)
    vote_reject = models.IntegerField('反对票', default=0)
    voters = models.JSONField('投票人列表', default=list, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    deadline = models.DateTimeField('截止时间', null=True, blank=True)

    class Meta:
        db_table = 'family_confirmation'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_confirm_type_display()}-{self.title}'
