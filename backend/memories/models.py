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


class CollectionTask(models.Model):
    TASK_TYPE_CHOICES = [
        ('identity_confirm', '人物身份确认'),
        ('old_name_supplement', '旧称/别名补充'),
        ('migration_supplement', '迁居信息补充'),
        ('event_narration', '事件背景口述'),
        ('relation_verify', '亲属关系校验'),
    ]
    SOURCE_TYPE_CHOICES = [
        ('photo', '照片'),
        ('person', '人物'),
        ('memory', '回忆片段'),
    ]
    STATUS_CHOICES = [
        ('open', '待认领'),
        ('assigned', '已分派待完成'),
        ('in_progress', '处理中'),
        ('submitted', '待审核'),
        ('completed', '已完成'),
        ('rejected', '已驳回'),
        ('conflicted', '进入确认台'),
    ]
    ASSIGN_TYPE_CHOICES = [
        ('family', '全家开放'),
        ('specific', '指定人员'),
    ]

    task_type = models.CharField('任务类型', max_length=30, choices=TASK_TYPE_CHOICES)
    title = models.CharField('任务标题', max_length=300)
    description = models.TextField('任务描述', blank=True)
    source_type = models.CharField('来源类型', max_length=20, choices=SOURCE_TYPE_CHOICES)
    related_photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    related_person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    related_memory = models.ForeignKey(MemoryFragment, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    extra_context = models.JSONField('补充上下文', default=dict, blank=True, help_text='如位置信息、人物ID等')
    assign_type = models.CharField('分派方式', max_length=20, choices=ASSIGN_TYPE_CHOICES, default='family')
    assigned_to = models.CharField('分派对象', max_length=100, blank=True, help_text='指定家属时填写姓名')
    claimed_by = models.CharField('认领人', max_length=100, blank=True)
    status = models.CharField('任务状态', max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.IntegerField('优先级', default=0, help_text='数值越大优先级越高')
    created_by = models.CharField('创建人', max_length=100, default='系统')
    due_date = models.DateTimeField('截止时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    claimed_at = models.DateTimeField('认领时间', null=True, blank=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'collection_task'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f'{self.get_task_type_display()}-{self.title}'


class TaskSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
        ('conflicted', '进入确认台'),
    ]

    task = models.ForeignKey(CollectionTask, on_delete=models.CASCADE, related_name='submissions', verbose_name='所属任务')
    submitter = models.CharField('提交人', max_length=100)
    submission_data = models.JSONField('提交内容数据', default=dict, help_text='根据任务类型存储不同结构的数据')
    submission_text = models.TextField('文本内容', blank=True, help_text='口述或长文本内容')
    has_conflict = models.BooleanField('是否有冲突', default=False)
    conflict_description = models.TextField('冲突说明', blank=True)
    status = models.CharField('审核状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewer = models.CharField('审核人', max_length=100, blank=True)
    review_comment = models.TextField('审核意见', blank=True)
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    related_conflict = models.ForeignKey(ConflictVersion, on_delete=models.SET_NULL, null=True, blank=True, related_name='submissions')
    related_confirmation = models.ForeignKey(FamilyConfirmation, on_delete=models.SET_NULL, null=True, blank=True, related_name='submissions')
    created_at = models.DateTimeField('提交时间', auto_now_add=True)

    class Meta:
        db_table = 'task_submission'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task}-{self.submitter}-{self.get_status_display()}'


class Contribution(models.Model):
    TYPE_CHOICES = [
        ('task_submit', '任务提交'),
        ('task_claim', '任务认领'),
        ('task_approved', '任务审核通过'),
        ('clue_claim', '线索认领'),
        ('person_add', '人物建档'),
        ('memory_add', '回忆添加'),
        ('photo_annotate', '照片补注'),
        ('review_pass', '审核通过'),
        ('vote_participate', '参与投票'),
    ]

    contributor = models.CharField('贡献人', max_length=100)
    contribution_type = models.CharField('贡献类型', max_length=30, choices=TYPE_CHOICES)
    related_task = models.ForeignKey(CollectionTask, on_delete=models.SET_NULL, null=True, blank=True, related_name='contributions')
    related_person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='contributions')
    related_photo = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True, blank=True, related_name='contributions')
    related_memory = models.ForeignKey(MemoryFragment, on_delete=models.SET_NULL, null=True, blank=True, related_name='contributions')
    description = models.CharField('贡献描述', max_length=500, blank=True)
    points = models.IntegerField('贡献积分', default=10)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'contribution'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.contributor}-{self.get_contribution_type_display()}-{self.points}分'


class StandardizedLocation(models.Model):
    LEVEL_CHOICES = [
        ('country', '国家'),
        ('province', '省/直辖市'),
        ('city', '市'),
        ('district', '区/县'),
        ('town', '乡镇/街道'),
        ('village', '村/社区'),
        ('detail', '详细地址'),
    ]

    original_name = models.CharField('原始地点名称', max_length=500)
    standardized_name = models.CharField('标准化地点名称', max_length=500, blank=True)
    level = models.CharField('地点层级', max_length=20, choices=LEVEL_CHOICES, default='detail')
    country = models.CharField('国家', max_length=100, blank=True, default='中国')
    province = models.CharField('省/直辖市', max_length=100, blank=True)
    city = models.CharField('市', max_length=100, blank=True)
    district = models.CharField('区/县', max_length=100, blank=True)
    town = models.CharField('乡镇/街道', max_length=100, blank=True)
    village = models.CharField('村/社区', max_length=100, blank=True)
    detail = models.CharField('详细地址', max_length=300, blank=True)
    latitude = models.FloatField('纬度', null=True, blank=True)
    longitude = models.FloatField('经度', null=True, blank=True)
    alias_names = models.JSONField('别名列表', default=list, blank=True)
    is_verified = models.BooleanField('是否已确认', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'standardized_location'
        ordering = ['province', 'city', 'district']
        indexes = [
            models.Index(fields=['original_name']),
            models.Index(fields=['standardized_name']),
            models.Index(fields=['province', 'city']),
        ]

    def __str__(self):
        return self.standardized_name or self.original_name

    def get_full_address(self):
        parts = [self.country, self.province, self.city, self.district, self.town, self.village, self.detail]
        return ''.join([p for p in parts if p])


class TimelineNode(models.Model):
    NODE_TYPE_CHOICES = [
        ('birth', '出生'),
        ('death', '逝世'),
        ('migration', '迁居'),
        ('photo', '照片拍摄'),
        ('memory', '回忆事件'),
        ('event', '重要事件'),
        ('task_result', '采集任务结果'),
    ]
    SOURCE_TYPE_CHOICES = [
        ('migration_info', '迁居记录'),
        ('photo', '照片'),
        ('memory', '回忆片段'),
        ('person', '人物档案'),
        ('task_submission', '采集任务提交'),
        ('manual', '手动添加'),
    ]
    STATUS_CHOICES = [
        ('confirmed', '已确认（正式时间线）'),
        ('pending', '待确认'),
        ('conflicted', '存在冲突'),
        ('rejected', '已驳回'),
    ]
    CONFLICT_FIELD_CHOICES = [
        ('location', '地点冲突'),
        ('year', '年份冲突'),
        ('both', '地点+年份冲突'),
        ('none', '无冲突'),
    ]

    node_type = models.CharField('节点类型', max_length=30, choices=NODE_TYPE_CHOICES)
    source_type = models.CharField('数据来源', max_length=30, choices=SOURCE_TYPE_CHOICES)
    source_id = models.IntegerField('来源记录ID', null=True, blank=True)

    related_person = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=True, blank=True,
        related_name='timeline_nodes', verbose_name='关联人物'
    )
    related_photo = models.ForeignKey(
        Photo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='timeline_nodes', verbose_name='关联照片'
    )
    related_memory = models.ForeignKey(
        MemoryFragment, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='timeline_nodes', verbose_name='关联回忆'
    )
    related_migration = models.ForeignKey(
        MigrationInfo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='timeline_nodes', verbose_name='关联迁居记录'
    )
    related_conflict = models.ForeignKey(
        ConflictVersion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='timeline_nodes', verbose_name='关联冲突版本'
    )

    title = models.CharField('节点标题', max_length=300)
    description = models.TextField('节点描述', blank=True)

    original_location = models.CharField('原始地点', max_length=500, blank=True)
    location = models.ForeignKey(
        StandardizedLocation, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='timeline_nodes', verbose_name='标准化地点'
    )
    from_location = models.ForeignKey(
        StandardizedLocation, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='timeline_nodes_from', verbose_name='迁出地（迁居用）'
    )

    year = models.IntegerField('年份', null=True, blank=True)
    month = models.IntegerField('月份', null=True, blank=True)
    day = models.IntegerField('日期', null=True, blank=True)
    decade = models.CharField('年代', max_length=20, blank=True, help_text='如：1980s')
    year_unknown = models.BooleanField('年份未知', default=False)

    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    conflict_field = models.CharField('冲突类型', max_length=10, choices=CONFLICT_FIELD_CHOICES, default='none')
    conflict_version_group = models.CharField('冲突版本组ID', max_length=50, blank=True, help_text='同一事件的冲突版本共用此ID')

    extra_data = models.JSONField('额外数据', default=dict, blank=True)
    created_by = models.CharField('创建人', max_length=100, default='系统')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'timeline_node'
        ordering = ['-year', '-month', '-day', '-created_at']
        indexes = [
            models.Index(fields=['related_person', 'year']),
            models.Index(fields=['node_type', 'status']),
            models.Index(fields=['location']),
            models.Index(fields=['decade']),
            models.Index(fields=['conflict_version_group']),
        ]

    def __str__(self):
        year_str = f'{self.year}年' if self.year else '年份不详'
        loc_str = self.original_location or (self.location.standardized_name if self.location else '地点不详')
        return f'{year_str} {loc_str} - {self.title}'

    def get_sort_key(self):
        return (
            self.year or 9999,
            self.month or 12,
            self.day or 31,
        )
