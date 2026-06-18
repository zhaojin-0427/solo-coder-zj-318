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

export const getOptionLabel = (options, value) => {
  const opt = options.find(o => o.value === value)
  return opt?.label || value
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
