import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'familymemories.settings')
django.setup()

from django.core.files.base import ContentFile
from memories.models import (
    Person, Alias, MigrationInfo, Relationship, Photo,
    PersonInPhoto, MemoryFragment, ConflictVersion, FamilyConfirmation
)

def seed_data():
    print('开始填充示例数据...')

    if Person.objects.exists():
        print('检测到已有数据，跳过填充')
        return

    persons_data = [
        {'id': 1, 'name': '李大山', 'gender': 'M', 'birth_year': 1915, 'death_year': 1998, 'birth_place': '山东青岛',
         'description': '家族第一代，年轻时闯关东到东北，后在沈阳定居。开过铁匠铺，为人正直豪爽。',
         'status': 'confirmed', 'created_by': '长孙'},
        {'id': 2, 'name': '王秀兰', 'gender': 'F', 'birth_year': 1922, 'death_year': 2010, 'birth_place': '辽宁沈阳',
         'description': '典型的东北妇女，养育了5个子女，一手好针线活。',
         'status': 'confirmed', 'created_by': '三姑'},
        {'id': 3, 'name': '李建国', 'gender': 'M', 'birth_year': 1948, 'death_year': None, 'birth_place': '辽宁沈阳',
         'description': '长子，18岁参军，后转业到天津纺织厂当干部。',
         'status': 'confirmed', 'created_by': '长子'},
        {'id': 4, 'name': '李建华', 'gender': 'M', 'birth_year': 1952, 'death_year': None, 'birth_place': '辽宁沈阳',
         'description': '二儿子，下乡知青，后回城在国企工作。',
         'status': 'confirmed', 'created_by': '本人'},
        {'id': 5, 'name': '李建梅', 'gender': 'F', 'birth_year': 1955, 'death_year': None, 'birth_place': '辽宁沈阳',
         'description': '大女儿，嫁给本地张家。',
         'status': 'pending', 'created_by': '大姑'},
        {'id': 6, 'name': '张桂芬', 'gender': 'F', 'birth_year': 1958, 'death_year': None, 'birth_place': '天津',
         'description': '长媳，李建国的妻子。',
         'status': 'confirmed', 'created_by': '小姑子'},
        {'id': 7, 'name': '李明', 'gender': 'M', 'birth_year': 1985, 'death_year': None, 'birth_place': '天津',
         'description': '长孙，李建国与张桂芬之子。',
         'status': 'pending', 'created_by': '奶奶'},
        {'id': 8, 'name': '未知老人', 'gender': 'U', 'birth_year': None, 'death_year': None, 'birth_place': '',
         'description': '老照片中出现，背面有模糊字迹，疑似李大山的弟弟。',
         'status': 'conflicted', 'created_by': '家属'}
    ]

    persons = {}
    for data in persons_data:
        p = Person.objects.create(**data)
        persons[p.id] = p
        print(f'  人物: {p.name}')

    aliases_data = [
        (1, {'alias_name': '老铁匠', 'usage_context': '街坊称呼', 'added_by': '长孙'}),
        (1, {'alias_name': '大山哥', 'usage_context': '同辈称呼', 'added_by': '三姑'}),
        (2, {'alias_name': '秀兰妹子', 'usage_context': '年轻时', 'added_by': '大姑'}),
        (3, {'alias_name': '大民子', 'usage_context': '乳名', 'added_by': '二弟'}),
        (4, {'alias_name': '二华', 'usage_context': '家中排行', 'added_by': '三弟'}),
        (6, {'alias_name': '大芬', 'usage_context': '婆家称呼', 'added_by': '小姑子'}),
        (7, {'alias_name': '明明', 'usage_context': '乳名', 'added_by': '奶奶'}),
    ]
    for pid, alias_data in aliases_data:
        Alias.objects.create(person=persons[pid], **alias_data)

    migrations_data = [
        (1, {'from_place': '山东青岛', 'to_place': '辽宁沈阳', 'move_year': 1934, 'reason': '闯关东谋生', 'added_by': '长孙'}),
        (3, {'from_place': '辽宁沈阳', 'to_place': '天津', 'move_year': 1970, 'reason': '部队转业分配', 'added_by': '长子'}),
        (4, {'from_place': '辽宁沈阳', 'to_place': '黑龙江北大荒', 'move_year': 1969, 'reason': '上山下乡', 'added_by': '本人'}),
        (4, {'from_place': '黑龙江北大荒', 'to_place': '辽宁沈阳', 'move_year': 1978, 'reason': '知青返城', 'added_by': '本人'}),
    ]
    for pid, mig_data in migrations_data:
        MigrationInfo.objects.create(person=persons[pid], **mig_data)

    rels = [
        (1, 2, 'spouse', '结发夫妻', '长孙'),
        (1, 3, 'child', '长子', '长孙'),
        (1, 4, 'child', '次子', '长孙'),
        (1, 5, 'child', '长女', '长孙'),
        (2, 3, 'child', '长子', '长孙'),
        (2, 4, 'child', '次子', '长孙'),
        (2, 5, 'child', '长女', '长孙'),
        (3, 6, 'spouse', '', '本人'),
        (3, 7, 'child', '独子', '本人'),
    ]
    for fp, tp, rt, note, ab in rels:
        Relationship.objects.create(
            from_person=persons[fp], to_person=persons[tp],
            relation_type=rt, relation_note=note, added_by=ab
        )

    photos_data = [
        {'title': '1952年父亲参军留影', 'era': '1950s', 'scene': 'military', 'source': 'old_album',
         'taken_year': 1952, 'location': '辽宁沈阳', 'status': 'completed', 'uploader': '长孙',
         'description': '父亲当年18岁，刚刚入伍，穿着借来的军装照的第一张照片。奶奶说这张照片她藏在枕头底下好几年。'},
        {'title': '1968年春节全家福', 'era': '1960s', 'scene': 'family_portrait', 'source': 'scanned',
         'taken_year': 1968, 'location': '山东青岛老家', 'status': 'annotating', 'uploader': '大姑',
         'description': '爷爷奶奶带着5个孩子，那年二叔刚从农村插队回来，全家好不容易凑齐。'},
        {'title': '母亲年轻时的工作照', 'era': '1970s', 'scene': 'work_school', 'source': 'old_album',
         'taken_year': 1975, 'location': '天津纺织厂', 'status': 'archived', 'uploader': '二舅',
         'description': '妈妈在车间当检验员，连年的三八红旗手。'},
        {'title': '1985年大哥结婚', 'era': '1980s', 'scene': 'wedding', 'source': 'old_album',
         'taken_year': 1985, 'location': '老家四合院', 'status': 'annotating', 'uploader': '三妹',
         'description': '那时候结婚还是在家办酒席，请了街坊四邻一共12桌。'},
        {'title': '90年代初第一次去北京', 'era': '1990s', 'scene': 'travel', 'source': 'family_donation',
         'taken_year': 1992, 'location': '北京天安门', 'status': 'archived', 'uploader': '二姐',
         'description': '爸妈金婚旅行，第一次坐火车出远门。'},
        {'title': '2005年家族大聚会', 'era': '2000s', 'scene': 'festival', 'source': 'digital_camera',
         'taken_year': 2005, 'location': '上海某酒店', 'status': 'completed', 'uploader': '长孙媳',
         'description': '爷爷90大寿，四代同堂共38人。'},
        {'title': '我小时候和外公', 'era': '1990s', 'scene': 'childhood', 'source': 'scanned',
         'taken_year': 1995, 'location': '', 'status': 'archived', 'uploader': '外孙',
         'description': ''},
        {'title': '2018年清明扫墓', 'era': '2010s', 'scene': 'other', 'source': 'phone',
         'taken_year': 2018, 'location': '苏州公墓', 'status': 'annotating', 'uploader': '堂弟',
         'description': '家人从各地赶来，祭扫后一起吃了团圆饭。'},
        {'title': '奶奶少女时代', 'era': '1930s', 'scene': 'daily_life', 'source': 'old_album',
         'taken_year': 1938, 'location': '南京', 'status': 'completed', 'uploader': '三姑',
         'description': '奶奶说这是她上学时最好的朋友拍的，那年她16岁。'},
        {'title': '年代不详的老照片', 'era': 'unknown', 'scene': 'other', 'source': 'old_album',
         'taken_year': None, 'location': '', 'status': 'archived', 'uploader': '家属',
         'description': '从旧相册夹层找到的，背面没有字，没人认得出来。'},
    ]
    photos = []
    for data in photos_data:
        ph = Photo.objects.create(**data)
        photos.append(ph)
        print(f'  照片: {ph.title}')

    pips = [
        (1, 3, None, '后排中间', '大山', '一家之主', '长孙'),
        (1, 2, None, '前排中间', '秀兰', '', '长孙'),
        (1, None, '二姑（待确认）', '前排右一', '二丫头', '14岁', '大姑'),
        (3, 3, None, '新郎', '建国', '28岁', '三妹'),
        (3, 6, None, '新娘', '桂芬', '25岁', '三妹'),
    ]
    for ph_idx, person_id, name_override, pos, old_title, role, ab in pips:
        ph = photos[ph_idx - 1]
        PersonInPhoto.objects.create(
            photo=ph,
            person=persons.get(person_id),
            person_name_override=name_override or '',
            position_note=pos, old_title=old_title, role_note=role, added_by=ab
        )

    memories_data = [
        {'title': '爷爷讲的闯关东故事', 'status': 'published', 'occur_year': 1934,
         'occur_place': '山东青岛 → 辽宁沈阳', 'author': '爷爷口述·长孙记录',
         'content': '爷爷说，1934年家乡闹饥荒，他只有19岁，带着奶奶和仅有的两双布鞋，跟着同乡从山东青岛出发，坐了三天三夜的闷罐车到沈阳。他说一路上看到无数人流离失所，有人倒在路上就再也没起来。下车时，口袋里只剩下半个窝头，但他攥着奶奶的手说，"只要人在，啥都能挣回来"。后来爷爷在沈阳开了铁匠铺，靠着手艺养活了一大家人。'},
        {'title': '二叔的北大荒知青岁月', 'status': 'published', 'occur_year': 1969,
         'occur_place': '黑龙江北大荒', 'author': '二叔口述·侄女记录',
         'content': '二叔1969年下乡到黑龙江北大荒，那一年他才17岁。他写信说，冬天最低零下40度，出门眉毛胡子都是白的。最苦的是春种，在冻土上刨地，手心都是血泡。最难忘的是1976年冬天，他和战友们冒着暴雪把粮食从地里抢收回来，干完活棉鞋都冻在脚上脱不下来。他说那十年虽然苦，但练就了这辈子不服输的性子。'},
        {'title': '1968年春节全家福背后的故事', 'status': 'submitted', 'occur_year': 1968,
         'occur_place': '山东青岛老家', 'author': '大姑回忆·长孙媳整理',
         'content': '大姑说，这张全家福是全家凑得最齐的一次。那年二叔刚从北大荒请假回来探亲，小姑还在邻县读高中特意赶回来。拍照前一天，奶奶蒸了三锅白面馒头，爷爷买了半斤猪头肉，全家像过年一样。拍照时，摄影师让大家"都笑一笑"，可小姑的眼泪差点掉下来——她知道第二天二叔就要回北大荒了。'},
        {'title': '关于1968年全家福的不同版本', 'status': 'conflicted', 'occur_year': 1968,
         'occur_place': '辽宁沈阳', 'author': '二叔本人',
         'content': '我记得当时是二叔参军回来，不是从北大荒回来。而且拍照地点是在沈阳，不是青岛老家。'},
        {'title': '妈妈在纺织厂当标兵的那些年', 'status': 'draft', 'occur_year': 1978,
         'occur_place': '天津纺织厂', 'author': '长孙回忆',
         'content': '妈妈1975年进天津纺织厂当检验员，因为眼力好、手又快，连续三年评上三八红旗手。她说最忙的时候，一个班要检验八千多个线锭，眼睛经常熬得通红。有一次厂里选她去北京参加表彰大会，她激动得一晚上没睡着，回来还给我们每个人都带了北京果脯。'},
        {'title': '大哥1985年的婚礼', 'status': 'published', 'occur_year': 1985,
         'occur_place': '老家四合院', 'author': '三妹回忆',
         'content': '大哥结婚那年，家里还是四合院，酒席就摆在院子里，请了村东头的王厨子。大姐记得，迎亲的队伍骑着8辆永久牌自行车，新娘穿的红棉袄是妈妈亲手缝的，领口还绣了一朵大牡丹。洞房里点着两根红烛，晚辈们闹洞房闹到后半夜，爷爷笑得合不拢嘴。'},
    ]
    for m_data in memories_data:
        MemoryFragment.objects.create(**m_data)
        print(f'  回忆: {m_data["title"]}')

    conflicts_data = [
        {'conflict_field': 'photo_date', 'related_photo': photos[1],
         'version_a': '1968年春节，大年初三拍摄', 'version_a_author': '大姑回忆',
         'version_b': '1969年春节，二叔请假从北大荒回来那次', 'version_b_author': '二叔本人',
         'description': '关于这张全家福的拍摄年份，大姑和二叔的记忆有出入。需要确认二叔从北大荒第一次回家探亲的确切年份。',
         'status': 'open'},
        {'conflict_field': 'person_relation', 'related_person': persons[8],
         'version_a': '这是李大山的亲弟弟，叫李大河', 'version_a_author': '三姑听奶奶说的',
         'version_b': '这是李大山的表哥，从山东来投奔的，住了半年就走了', 'version_b_author': '二叔听爷爷提过一次',
         'description': '老照片夹层中发现的照片，背面字迹模糊，疑似家中长辈。关于此人身份有两种说法。',
         'status': 'open'},
        {'conflict_field': 'photo_location', 'related_photo': photos[8],
         'version_a': '南京外婆家门口', 'version_a_author': '奶奶生前说过',
         'version_b': '南京女子中学门口', 'version_b_author': '大姑看照片上的校服',
         'description': '', 'status': 'open'},
    ]
    for c_data in conflicts_data:
        ConflictVersion.objects.create(**c_data)

    confirms_data = [
        {'confirm_type': 'conflict', 'title': '确认1968年全家福的拍摄年份',
         'detail': '版本A：1968年春节，大年初三拍摄（大姑回忆）\n\n版本B：1969年春节，二叔请假从北大荒回来那次（二叔本人）\n\n请各位家属结合照片中人物衣着、二叔返乡时间综合判断。',
         'proposer': '长孙', 'status': 'pending', 'vote_approve': 2, 'vote_reject': 1,
         'voters': ['大姑', '三妹', '二叔']},
        {'confirm_type': 'person', 'title': '确认"未知老人"的身份',
         'detail': '老照片夹层中发现的照片，背面有模糊字迹"大河边"。\n\n说法一：李大山的亲弟弟李大河\n说法二：李大山的表哥，从山东来投奔。\n\n请老一辈家属回忆并确认。',
         'proposer': '长孙媳', 'status': 'pending', 'vote_approve': 1, 'vote_reject': 2,
         'voters': ['三姑', '二叔', '大姑']},
        {'confirm_type': 'memory', 'title': '确认闯关东的出发年份',
         'detail': '关于爷爷闯关东的年份：\n\n说法一：1934年，爷爷19岁（长孙笔记）\n说法二：1936年，爷爷21岁（三姑印象）\n\n需要统一写入家族史。',
         'proposer': '长孙', 'status': 'approved', 'vote_approve': 4, 'vote_reject': 0,
         'voters': ['二叔', '大姑', '三姑', '大哥']},
        {'confirm_type': 'photo_person', 'title': '确认1985年婚礼照片中"后排左三"是谁',
         'detail': '1985年大哥婚礼照片，后排左三的年轻人身份存疑。\n\n说法一：新娘的表弟\n说法二：新郎的发小\n\n请当年在场的家属确认。',
         'proposer': '三妹', 'status': 'tied', 'vote_approve': 1, 'vote_reject': 1,
         'voters': ['大嫂', '三妹']},
        {'confirm_type': 'relation', 'title': '确认张桂芬与李建国的关系为"配偶"',
         'detail': '经晚辈整理，确认张桂芬（天津人，1958年生）为李建国的配偶，1980年结婚。请确认。',
         'proposer': '长孙媳整理', 'status': 'approved', 'vote_approve': 5, 'vote_reject': 0,
         'voters': ['李建国', '张桂芬', '大姑', '二叔', '三姑']},
    ]
    for data in confirms_data:
        FamilyConfirmation.objects.create(**data)

    print('✅ 示例数据填充完成！')
    print(f'  人物: {Person.objects.count()}人')
    print(f'  照片: {Photo.objects.count()}张')
    print(f'  回忆: {MemoryFragment.objects.count()}篇')
    print(f'  冲突: {ConflictVersion.objects.count()}条')
    print(f'  确认: {FamilyConfirmation.objects.count()}项')

if __name__ == '__main__':
    seed_data()
