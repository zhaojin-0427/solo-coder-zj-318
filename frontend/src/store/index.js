import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const stats = ref(null)
  const loading = ref(false)

  return { stats, loading }
})

export const ERA_OPTIONS = [
  { value: '1920s', label: '1920年代' },
  { value: '1930s', label: '1930年代' },
  { value: '1940s', label: '1940年代' },
  { value: '1950s', label: '1950年代' },
  { value: '1960s', label: '1960年代' },
  { value: '1970s', label: '1970年代' },
  { value: '1980s', label: '1980年代' },
  { value: '1990s', label: '1990年代' },
  { value: '2000s', label: '2000年代' },
  { value: '2010s', label: '2010年代' },
  { value: '2020s', label: '2020年代' },
  { value: 'unknown', label: '年代不详' }
]

export const SCENE_OPTIONS = [
  { value: 'family_portrait', label: '全家福' },
  { value: 'wedding', label: '婚礼' },
  { value: 'daily_life', label: '日常生活' },
  { value: 'festival', label: '节庆聚会' },
  { value: 'travel', label: '旅行出游' },
  { value: 'work_school', label: '工作/求学' },
  { value: 'childhood', label: '童年' },
  { value: 'military', label: '军旅' },
  { value: 'funeral', label: '丧葬/纪念' },
  { value: 'other', label: '其他' }
]

export const SOURCE_OPTIONS = [
  { value: 'old_album', label: '老相册' },
  { value: 'family_donation', label: '家人捐赠' },
  { value: 'scanned', label: '扫描翻拍' },
  { value: 'digital_camera', label: '数码相机' },
  { value: 'phone', label: '手机拍摄' },
  { value: 'social_media', label: '社交媒体' },
  { value: 'other', label: '其他来源' }
]

export const RELATION_OPTIONS = [
  { value: 'father', label: '父亲' },
  { value: 'mother', label: '母亲' },
  { value: 'spouse', label: '配偶' },
  { value: 'child', label: '子女' },
  { value: 'sibling', label: '兄弟姐妹' },
  { value: 'grandparent', label: '祖父母' },
  { value: 'grandchild', label: '孙辈' },
  { value: 'uncle_aunt', label: '叔伯/姑姨' },
  { value: 'nephew_niece', label: '侄/甥' },
  { value: 'cousin', label: '堂/表亲' },
  { value: 'in_law', label: '姻亲' },
  { value: 'other', label: '其他' }
]

export const STATUS_OPTIONS = [
  { value: 'confirmed', label: '已确认', type: 'success' },
  { value: 'pending', label: '待确认', type: 'warning' },
  { value: 'conflicted', label: '信息冲突', type: 'danger' }
]

export const PHOTO_STATUS_OPTIONS = [
  { value: 'archived', label: '已归档', type: 'info' },
  { value: 'annotating', label: '补注中', type: 'warning' },
  { value: 'completed', label: '补注完成', type: 'success' }
]

export const MEMORY_STATUS_OPTIONS = [
  { value: 'draft', label: '草稿', type: 'info' },
  { value: 'submitted', label: '待整理', type: 'warning' },
  { value: 'published', label: '已沉淀', type: 'success' },
  { value: 'conflicted', label: '内容冲突', type: 'danger' }
]

export const CONFIRM_TYPE_OPTIONS = [
  { value: 'person', label: '人物信息' },
  { value: 'relation', label: '亲属关系' },
  { value: 'photo_info', label: '照片信息' },
  { value: 'photo_person', label: '照片人物' },
  { value: 'memory', label: '回忆内容' },
  { value: 'conflict', label: '冲突版本' }
]

export const CONFLICT_FIELD_OPTIONS = [
  { value: 'person_name', label: '人物姓名' },
  { value: 'person_relation', label: '亲属关系' },
  { value: 'photo_date', label: '拍摄时间' },
  { value: 'photo_location', label: '拍摄地点' },
  { value: 'photo_people', label: '照片人物' },
  { value: 'memory_content', label: '回忆内容' },
  { value: 'other', label: '其他信息' }
]

export const TASK_TYPE_OPTIONS = [
  { value: 'identity_confirm', label: '人物身份确认', icon: 'User', color: '#3B82F6' },
  { value: 'old_name_supplement', label: '旧称/别名补充', icon: 'EditPen', color: '#F59E0B' },
  { value: 'migration_supplement', label: '迁居信息补充', icon: 'Location', color: '#8B5CF6' },
  { value: 'event_narration', label: '事件背景口述', icon: 'ChatDotRound', color: '#EC4899' },
  { value: 'relation_verify', label: '亲属关系校验', icon: 'Connection', color: '#10B981' }
]

export const TASK_SOURCE_OPTIONS = [
  { value: 'photo', label: '照片', icon: 'Picture' },
  { value: 'person', label: '人物', icon: 'User' },
  { value: 'memory', label: '回忆片段', icon: 'Document' }
]

export const TASK_STATUS_OPTIONS = [
  { value: 'open', label: '待认领', type: 'info', color: '#6B7280' },
  { value: 'assigned', label: '已分派', type: 'warning', color: '#F59E0B' },
  { value: 'in_progress', label: '处理中', type: 'warning', color: '#3B82F6' },
  { value: 'submitted', label: '待审核', type: 'warning', color: '#8B5CF6' },
  { value: 'completed', label: '已完成', type: 'success', color: '#10B981' },
  { value: 'rejected', label: '已驳回', type: 'danger', color: '#EF4444' },
  { value: 'conflicted', label: '进入确认台', type: 'danger', color: '#DC2626' }
]

export const TASK_ASSIGN_OPTIONS = [
  { value: 'family', label: '全家开放' },
  { value: 'specific', label: '指定人员' }
]

export const SUBMISSION_STATUS_OPTIONS = [
  { value: 'pending', label: '待审核', type: 'warning' },
  { value: 'approved', label: '已通过', type: 'success' },
  { value: 'rejected', label: '已驳回', type: 'danger' },
  { value: 'conflicted', label: '进入确认台', type: 'danger' }
]

export const CONTRIBUTION_TYPE_OPTIONS = [
  { value: 'task_submit', label: '任务提交', icon: 'Upload', points: 10 },
  { value: 'task_claim', label: '任务认领', icon: 'Check', points: 5 },
  { value: 'task_approved', label: '任务审核通过', icon: 'CircleCheckFilled', points: 30 },
  { value: 'clue_claim', label: '线索认领', icon: 'Search', points: 20 },
  { value: 'person_add', label: '人物建档', icon: 'UserPlus', points: 25 },
  { value: 'memory_add', label: '回忆添加', icon: 'Plus', points: 35 },
  { value: 'photo_annotate', label: '照片补注', icon: 'Edit', points: 15 },
  { value: 'review_pass', label: '审核通过', icon: 'Promotion', points: 20 },
  { value: 'vote_participate', label: '参与投票', icon: 'Star', points: 5 }
]

export const CURRENT_USER = '家属李明'

export const getOptionLabel = (options, value) => {
  const opt = options.find(o => o.value === value)
  return opt?.label || value
}

export const getTaskTypeInfo = (value) => {
  return TASK_TYPE_OPTIONS.find(o => o.value === value) || TASK_TYPE_OPTIONS[0]
}

export const getTaskStatusInfo = (value) => {
  return TASK_STATUS_OPTIONS.find(o => o.value === value) || TASK_STATUS_OPTIONS[0]
}

export const photoPlaceholder = (era, scene) => {
  const scenes = {
    family_portrait: '👨‍👩‍👧‍👦',
    wedding: '💒',
    daily_life: '🏠',
    festival: '🎊',
    travel: '🏞️',
    work_school: '🏫',
    childhood: '🧒',
    military: '🎖️',
    funeral: '🕯️',
    other: '📷'
  }
  return scenes[scene] || '📷'
}
