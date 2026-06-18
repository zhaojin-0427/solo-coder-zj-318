<template>
  <div class="memories-page">
    <div class="page-header">
      <div class="page-title">
        <el-icon><Document /></el-icon>
        回忆片段整理
      </div>
      <div class="page-subtitle">老人口述、晚辈撰写、事件记录...将零散的回忆片段沉淀为完整的家族故事</div>
    </div>

    <div class="card-warm" style="padding: 20px; margin-bottom: 20px;">
      <div class="filter-row">
        <el-input v-model="searchText" placeholder="搜索回忆标题、内容..." style="width: 280px;" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterStatus" placeholder="按状态" clearable style="width: 140px">
          <el-option v-for="s in MEMORY_STATUS_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="filterAuthor" placeholder="按讲述人" clearable filterable style="width: 160px">
          <el-option v-for="a in authors" :key="a" :label="a" :value="a" />
        </el-select>
        <div style="flex: 1"></div>
        <el-button type="primary" class="btn-primary-warm" @click="showAdd = true">
          <el-icon><EditPen /></el-icon>撰写回忆
        </el-button>
      </div>
    </div>

    <div class="status-stat-row">
      <div class="status-stat draft" :class="{active: statusFilter === 'draft'}" @click="setFilter('draft')">
        <div class="stat-num">{{ counts.draft }}</div>
        <div class="stat-label">草稿</div>
      </div>
      <div class="status-stat submitted" :class="{active: statusFilter === 'submitted'}" @click="setFilter('submitted')">
        <div class="stat-num">{{ counts.submitted }}</div>
        <div class="stat-label">待整理</div>
      </div>
      <div class="status-stat published" :class="{active: statusFilter === 'published'}" @click="setFilter('published')">
        <div class="stat-num">{{ counts.published }}</div>
        <div class="stat-label">已沉淀</div>
      </div>
      <div class="status-stat conflicted" :class="{active: statusFilter === 'conflicted'}" @click="setFilter('conflicted')">
        <div class="stat-num">{{ counts.conflicted }}</div>
        <div class="stat-label">有冲突</div>
      </div>
      <div class="status-stat all" :class="{active: statusFilter === ''}" @click="setFilter('')">
        <div class="stat-num">{{ memories.length }}</div>
        <div class="stat-label">全部</div>
      </div>
    </div>

    <div class="memories-timeline" v-loading="loading">
      <el-empty v-if="!filteredMemories.length && !loading" description="还没有回忆，开始记录第一个家族故事吧" />
      <div v-for="m in filteredMemories" :key="m.id" class="memory-card card-warm" @click="openDetail(m)">
        <div class="memory-header">
          <div class="memory-title-row">
            <h3 class="memory-title">{{ m.title }}</h3>
            <el-tag size="small" :type="getStatusType(m.status)" effect="light">
              {{ getOptionLabel(MEMORY_STATUS_OPTIONS, m.status) }}
            </el-tag>
          </div>
          <div class="memory-meta">
            <span v-if="m.occur_year" class="meta-item"><el-icon><Calendar /></el-icon> {{ m.occur_year }}年</span>
            <span v-if="m.occur_place" class="meta-item"><el-icon><Location /></el-icon> {{ m.occur_place }}</span>
            <span class="meta-item"><el-icon><User /></el-icon> {{ m.author }}</span>
            <span class="meta-item"><el-icon><Clock /></el-icon> {{ formatDate(m.created_at) }}</span>
          </div>
        </div>
        <div class="memory-content-preview">{{ m.content }}</div>
        <div class="memory-footer">
          <div class="linked-assets">
            <div v-if="m.related_photos_detail?.length || m.related_photos_count" class="linked-item">
              <el-icon><Picture /></el-icon>
              <span>关联照片 {{ m.related_photos_count || m.related_photos_detail?.length || 0 }}张</span>
              <div class="linked-photos">
                <div v-for="i in Math.min(m.related_photos_count || m.related_photos_detail?.length || 0, 4)" :key="i" class="linked-photo-thumb">📷</div>
              </div>
            </div>
            <div v-if="m.related_people_detail?.length || m.related_people_count" class="linked-item">
              <el-icon><UserFilled /></el-icon>
              <span>关联人物</span>
              <div class="linked-persons">
                <el-tag v-for="p in (m.related_people_detail || []).slice(0,4)" :key="p.id" size="small" effect="plain">
                  {{ p.name }}
                </el-tag>
                <span v-if="(m.related_people_count || 0) > 4" class="more-count">
                  +{{ m.related_people_count - 4 }}人
                </span>
              </div>
            </div>
            <div class="linked-item" :style="{ cursor: 'pointer' }" @click.stop="viewMemoryTasks(m)">
              <el-icon color="#D2691E"><List /></el-icon>
              <span style="color:#8B4513;font-weight:500;">采集任务</span>
              <el-tag v-if="getMemoryTaskCount(m.id)" size="small" type="warning" effect="light">
                {{ getMemoryTaskCount(m.id) }} 项
              </el-tag>
              <el-tag v-else size="small" effect="plain">发起</el-tag>
            </div>
          </div>
          <div class="memory-actions" @click.stop>
            <el-button size="small" plain @click="openDetail(m)">
              <el-icon><View /></el-icon>查看
            </el-button>
            <el-button size="small" type="primary" plain @click="editMemory(m)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button size="small" type="warning" plain @click="openCreateTaskFromCard(m)">
              <el-icon><EditPen /></el-icon>发起补注
            </el-button>
            <el-button size="small" @click="publishMemory(m)" v-if="m.status !== 'published'">
              <el-icon><CircleCheck /></el-icon>沉淀
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAdd" :title="editingMemory ? '编辑回忆' : '撰写回忆片段'" width="720px" destroy-on-close>
      <el-form :model="memoryForm" label-width="100px">
        <el-form-item label="回忆标题" required>
          <el-input v-model="memoryForm.title" placeholder="如：爷爷讲的闯关东故事" />
        </el-form-item>
        <el-form-item label="发生年份">
          <el-input-number v-model="memoryForm.occur_year" :min="1850" :max="2030" />
        </el-form-item>
        <el-form-item label="发生地点">
          <el-input v-model="memoryForm.occur_place" placeholder="如：山东青岛李村" />
        </el-form-item>
        <el-form-item label="回忆内容" required>
          <el-input v-model="memoryForm.content" type="textarea" :rows="8" placeholder="记录下完整的故事细节...老人口述的原话、晚辈的补充、当时的场景描写" />
        </el-form-item>
        <el-form-item label="讲述/撰写人">
          <el-input v-model="memoryForm.author" placeholder="如：爷爷口述·长孙记录" />
        </el-form-item>
        <el-form-item label="关联照片">
          <el-select v-model="linkedPhotos" multiple filterable placeholder="选择关联的照片" style="width: 100%">
            <el-option v-for="p in allPhotos" :key="p.id" :label="p.title || `照片#${p.id}`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联人物">
          <el-select v-model="linkedPersons" multiple filterable placeholder="选择关联的人物" style="width: 100%">
            <el-option v-for="p in allPersons" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="整理状态">
          <el-radio-group v-model="memoryForm.status">
            <el-radio v-for="s in MEMORY_STATUS_OPTIONS" :key="s.value" :value="s.value">{{ s.label }}</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitMemory">保存回忆</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetail" :title="detail?.title" width="800px" destroy-on-close>
      <div v-if="detail" class="memory-detail">
        <div class="detail-meta-row">
          <el-tag size="small" type="info" v-if="detail.occur_year">{{ detail.occur_year }}年</el-tag>
          <el-tag size="small" effect="plain" v-if="detail.occur_place">📍 {{ detail.occur_place }}</el-tag>
          <el-tag size="small" effect="plain">✍️ {{ detail.author }}</el-tag>
          <el-tag size="small" :type="getStatusType(detail.status)" effect="light">
            {{ getOptionLabel(MEMORY_STATUS_OPTIONS, detail.status) }}
          </el-tag>
        </div>
        <div class="detail-content-text">
          {{ detail.content }}
        </div>
        <div class="detail-link-section" v-if="detail.related_photos_detail?.length">
          <h4><el-icon><Picture /></el-icon> 关联照片</h4>
          <div class="detail-photo-grid">
            <div v-for="p in detail.related_photos_detail" :key="p.id" class="detail-photo">
              <div class="dp-thumb">📷</div>
              <div class="dp-title">{{ p.title }}</div>
              <div class="dp-meta">{{ p.era_display }} · {{ p.scene_display }}</div>
            </div>
          </div>
        </div>
        <div class="detail-link-section" v-if="detail.related_people_detail?.length">
          <h4><el-icon><UserFilled /></el-icon> 关联人物</h4>
          <div class="detail-person-tags">
            <el-tag v-for="p in detail.related_people_detail" :key="p.id" size="large" effect="light" type="warning">
              {{ p.name }}
            </el-tag>
          </div>
        </div>
        <div class="detail-link-section task-detail-section">
          <div class="section-header-row">
            <h4><el-icon color="#D2691E"><List /></el-icon> 关联采集任务</h4>
            <div class="section-actions">
              <el-button size="small" type="warning" plain @click="openCreateTaskFromDetail">
                <el-icon><EditPen /></el-icon>发起事件口述
              </el-button>
              <el-button size="small" @click="viewMemoryTasks(detail)">
                <el-icon><ArrowRight /></el-icon>查看全部
              </el-button>
            </div>
          </div>
          <div v-if="currentDetailTasks.length" class="detail-task-list">
            <div v-for="t in currentDetailTasks" :key="t.id" class="detail-task-item" @click="goToTaskDetail(t)">
              <el-tag :type="getTaskTypeInfo(t.task_type).tagType" size="small" effect="light">
                {{ getTaskTypeInfo(t.task_type).icon }} {{ getTaskTypeInfo(t.task_type).label }}
              </el-tag>
              <span class="dti-title">{{ t.title }}</span>
              <el-tag :type="getTaskStatusInfo(t.status).type" size="small">{{ getTaskStatusInfo(t.status).label }}</el-tag>
            </div>
          </div>
          <el-empty v-else description="暂无采集任务，可发起事件口述补注" :image-size="60" />
        </div>
        <div class="detail-time">
          记录时间：{{ formatDate(detail.created_at) }} · 最后更新：{{ formatDate(detail.updated_at) }}
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetail = false">关闭</el-button>
        <el-button @click="editMemory(detail)">编辑</el-button>
        <el-button type="primary" class="btn-primary-warm" v-if="detail?.status !== 'published'" @click="publishMemory(detail)">
          标记为已沉淀
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showTaskDialog" title="发起采集任务" width="560px" destroy-on-close>
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务类型" required>
          <el-select v-model="taskForm.task_type" style="width: 100%">
            <el-option
              v-for="opt in TASK_TYPE_OPTIONS.filter(t => ['event_narration', 'relation_verify', 'identity_confirm'].includes(t.value))"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="任务标题" required>
          <el-input v-model="taskForm.title" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="分派方式">
          <el-radio-group v-model="taskForm.assign_type">
            <el-radio value="open">全家认领</el-radio>
            <el-radio value="assigned">指定家属</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="指定家属" v-if="taskForm.assign_type === 'assigned'">
          <el-select v-model="taskForm.assigned_to" filterable placeholder="选择一位家属" style="width: 100%">
            <el-option v-for="p in allPersons" :key="p.id" :label="p.name" :value="p.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="taskForm.priority" style="width: 100%">
            <el-option label="普通" value="normal" />
            <el-option label="较高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitCreateTask">创建任务</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Document, Search, EditPen, Calendar, Location, User, Clock,
  Picture, UserFilled, View, Edit, CircleCheck, List, ArrowRight
} from '@element-plus/icons-vue'
import { memories as memApi, photos as photoApi, persons as personApi, tasks as tasksApi } from '@/api'
import { MEMORY_STATUS_OPTIONS, getOptionLabel, TASK_TYPE_OPTIONS, TASK_STATUS_OPTIONS, getTaskTypeInfo, getTaskStatusInfo, CURRENT_USER } from '@/store'

const loading = ref(false)
const memories = ref([])
const allPhotos = ref([])
const allPersons = ref([])
const searchText = ref('')
const filterStatus = ref('')
const filterAuthor = ref('')
const statusFilter = ref('')
const showAdd = ref(false)
const showDetail = ref(false)
const detail = ref(null)
const editingMemory = ref(null)
const linkedPhotos = ref([])
const linkedPersons = ref([])
const memoryForm = ref({
  title: '', occur_year: null, occur_place: '', content: '',
  author: '', status: 'draft'
})
const showTaskDialog = ref(false)
const taskForm = ref({ task_type: '', title: '', description: '', assign_type: 'open', assigned_to: '', priority: 'normal' })
const allTasks = ref([])
const currentDetailTasks = ref([])
const taskTargetMemory = ref(null)
const router = useRouter()

const authors = computed(() => [...new Set(memories.value.map(m => m.author).filter(Boolean))])

const counts = computed(() => ({
  draft: memories.value.filter(m => m.status === 'draft').length,
  submitted: memories.value.filter(m => m.status === 'submitted').length,
  published: memories.value.filter(m => m.status === 'published').length,
  conflicted: memories.value.filter(m => m.status === 'conflicted').length
}))

const filteredMemories = computed(() => {
  let r = memories.value
  if (statusFilter.value) r = r.filter(m => m.status === statusFilter.value)
  if (filterStatus.value) r = r.filter(m => m.status === filterStatus.value)
  if (filterAuthor.value) r = r.filter(m => m.author === filterAuthor.value)
  if (searchText.value) {
    const kw = searchText.value.toLowerCase()
    r = r.filter(m =>
      (m.title || '').toLowerCase().includes(kw) ||
      (m.content || '').toLowerCase().includes(kw)
    )
  }
  return r
})

const getStatusType = (s) => {
  const map = { draft: 'info', submitted: 'warning', published: 'success', conflicted: 'danger' }
  return map[s] || 'info'
}

const formatDate = (d) => {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`
}

const setFilter = (s) => { statusFilter.value = statusFilter.value === s ? '' : s }

const loadData = async () => {
  loading.value = true
  try {
    const [mRes, pRes, perRes, tRes] = await Promise.all([
      memApi.list({ page_size: 200 }).catch(() => ({ results: mockMemories() })),
      photoApi.simple().catch(() => []),
      personApi.simple().catch(() => []),
      tasksApi.list({ source_type: 'memory', page_size: 200 }).catch(() => ({ results: mockAllMemoryTasks() }))
    ])
    memories.value = mRes.results || mRes || mockMemories()
    allPhotos.value = pRes.results || pRes || []
    allPersons.value = perRes.results || perRes || []
    allTasks.value = tRes.results || tRes || mockAllMemoryTasks()
  } catch (e) {
    memories.value = mockMemories()
    allTasks.value = mockAllMemoryTasks()
  } finally {
    loading.value = false
  }
}

const openDetail = async (m) => {
  try {
    detail.value = await memApi.get(m.id)
  } catch (e) {
    detail.value = enrichMemory(m)
  }
  taskTargetMemory.value = detail.value
  loadDetailTasks(m.id)
  showDetail.value = true
}

const loadDetailTasks = async (memoryId) => {
  try {
    const res = await tasksApi.list({ source_type: 'memory', related_memory: memoryId, page_size: 20 })
    currentDetailTasks.value = res.results || res || []
  } catch (e) {
    currentDetailTasks.value = allTasks.value.filter(t => t.related_memory === memoryId)
  }
}

const loadAllTasks = async () => {
  try {
    const res = await tasksApi.list({ source_type: 'memory', page_size: 200 })
    allTasks.value = res.results || res || []
  } catch (e) {
    allTasks.value = mockAllMemoryTasks()
  }
}

const getMemoryTaskCount = (memoryId) => {
  return allTasks.value.filter(t => t.related_memory === memoryId).length
}

const viewMemoryTasks = (m) => {
  router.push({ path: '/tasks', query: { source_type: 'memory', related_id: m.id } })
}

const goToTaskDetail = () => {
  router.push('/tasks')
}

const openCreateTaskFromCard = (m) => {
  taskTargetMemory.value = m
  const typeInfo = getTaskTypeInfo('event_narration')
  taskForm.value = {
    task_type: 'event_narration',
    title: `【${typeInfo.label}】${m.title}`,
    description: `请为这段回忆补充更多口述细节或不同版本的叙述。\n回忆标题：${m.title}\n当前内容摘要：${(m.content || '').substring(0, 100)}...`,
    assign_type: 'open',
    assigned_to: '',
    priority: 'normal'
  }
  showTaskDialog.value = true
}

const openCreateTaskFromDetail = () => {
  if (!detail.value) return
  openCreateTaskFromCard(detail.value)
  showDetail.value = false
}

const submitCreateTask = async () => {
  if (!taskForm.value.title) { ElMessage.warning('请填写任务标题'); return }
  const mem = taskTargetMemory.value || detail.value
  try {
    const data = {
      ...taskForm.value,
      source_type: 'memory',
      related_memory: mem?.id,
      created_by: CURRENT_USER,
      status: taskForm.value.assign_type === 'assigned' && taskForm.value.assigned_to ? 'assigned' : 'open'
    }
    await tasksApi.create(data)
    ElMessage.success('采集任务已创建')
    showTaskDialog.value = false
    loadAllTasks()
    if (detail.value && mem?.id === detail.value.id) loadDetailTasks(mem.id)
  } catch (e) {
    allTasks.value.unshift({
      id: Date.now(),
      ...taskForm.value,
      source_type: 'memory',
      related_memory: mem?.id,
      status: taskForm.value.assign_type === 'assigned' && taskForm.value.assigned_to ? 'assigned' : 'open',
      created_at: new Date().toISOString()
    })
    ElMessage.success('采集任务已创建（模拟）')
    showTaskDialog.value = false
    if (detail.value && mem?.id === detail.value.id) loadDetailTasks(mem.id)
  }
}

const editMemory = (m) => {
  editingMemory.value = m
  memoryForm.value = {
    title: m.title, occur_year: m.occur_year, occur_place: m.occur_place,
    content: m.content, author: m.author, status: m.status
  }
  linkedPhotos.value = (m.related_photos_detail || []).map(p => p.id)
  linkedPersons.value = (m.related_people_detail || []).map(p => p.id)
  showDetail.value = false
  showAdd.value = true
}

const publishMemory = async (m) => {
  try {
    await memApi.update(m.id, { ...m, status: 'published' })
    ElMessage.success('已标记为已沉淀')
  } catch (e) {
    const target = memories.value.find(x => x.id === m.id)
    if (target) target.status = 'published'
    ElMessage.success('已标记为已沉淀（模拟）')
  }
  loadData()
}

const submitMemory = async () => {
  if (!memoryForm.value.title || !memoryForm.value.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  const submitData = {
    ...memoryForm.value,
    related_photos: linkedPhotos.value,
    related_people: linkedPersons.value
  }
  try {
    let res
    if (editingMemory.value) {
      res = await memApi.update(editingMemory.value.id, submitData)
    } else {
      res = await memApi.create(submitData)
    }
    ElMessage.success(editingMemory.value ? '回忆已更新' : '回忆已保存')
    await loadData()
  } catch (e) {
    const related_photos_detail = allPhotos.value.filter(p => linkedPhotos.value.includes(p.id))
    const related_people_detail = allPersons.value.filter(p => linkedPersons.value.includes(p.id))
    if (editingMemory.value) {
      const idx = memories.value.findIndex(x => x.id === editingMemory.value.id)
      if (idx > -1) memories.value[idx] = { ...memories.value[idx], ...memoryForm.value, related_photos_detail, related_people_detail }
    } else {
      memories.value.unshift({
        id: Date.now(), ...memoryForm.value,
        related_photos_detail, related_people_detail,
        related_photos_count: linkedPhotos.value.length,
        related_people_count: linkedPersons.value.length,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
    }
    ElMessage.success(editingMemory.value ? '回忆已更新（模拟）' : '回忆已保存（模拟）')
  }
  showAdd.value = false
  editingMemory.value = null
  memoryForm.value = { title: '', occur_year: null, occur_place: '', content: '', author: '', status: 'draft' }
  linkedPhotos.value = []
  linkedPersons.value = []
}

onMounted(loadData)
</script>

<script>
function mockMemories() {
  return [
    {
      id: 1,
      title: '爷爷讲的闯关东故事',
      content: '爷爷说，1934年家乡闹饥荒，他只有19岁，带着奶奶和仅有的两双布鞋，跟着同乡从山东青岛出发，坐了三天三夜的闷罐车到沈阳。他说一路上看到无数人流离失所，有人倒在路上就再也没起来。下车时，口袋里只剩下半个窝头，但他攥着奶奶的手说，"只要人在，啥都能挣回来"。后来爷爷在沈阳开了铁匠铺，靠着手艺养活了一大家人。',
      occur_year: 1934,
      occur_place: '山东青岛 → 辽宁沈阳',
      author: '爷爷口述·长孙记录',
      status: 'published',
      related_photos_count: 3,
      related_people_count: 2,
      related_photos_detail: [{ id: 1, title: '1952年父亲参军留影', era_display: '1950年代', scene_display: '军旅' }],
      related_people_detail: [{ id: 1, name: '李大山' }, { id: 2, name: '王秀兰' }],
      created_at: '2024-01-15T10:30:00',
      updated_at: '2024-02-20T14:15:00'
    },
    {
      id: 2,
      title: '二叔的北大荒知青岁月',
      content: '二叔1969年下乡到黑龙江北大荒，那一年他才17岁。他写信说，冬天最低零下40度，出门眉毛胡子都是白的。最苦的是春种，在冻土上刨地，手心都是血泡。最难忘的是1976年冬天，他和战友们冒着暴雪把粮食从地里抢收回来，干完活棉鞋都冻在脚上脱不下来。他说那十年虽然苦，但练就了这辈子不服输的性子。',
      occur_year: 1969,
      occur_place: '黑龙江北大荒',
      author: '二叔口述·侄女记录',
      status: 'published',
      related_photos_count: 2,
      related_people_count: 1,
      related_photos_detail: [],
      related_people_detail: [{ id: 4, name: '李建华' }],
      created_at: '2024-02-10T08:45:00',
      updated_at: '2024-02-10T08:45:00'
    },
    {
      id: 3,
      title: '1968年春节全家福背后的故事',
      content: '大姑说，这张全家福是全家凑得最齐的一次。那年二叔刚从北大荒请假回来探亲，小姑还在邻县读高中特意赶回来。拍照前一天，奶奶蒸了三锅白面馒头，爷爷买了半斤猪头肉，全家像过年一样。拍照时，摄影师让大家"都笑一笑"，可小姑的眼泪差点掉下来——她知道第二天二叔就要回北大荒了。',
      occur_year: 1968,
      occur_place: '山东青岛老家',
      author: '大姑回忆·长孙媳整理',
      status: 'submitted',
      related_photos_count: 1,
      related_people_count: 7,
      related_photos_detail: [{ id: 2, title: '1968年春节全家福', era_display: '1960年代', scene_display: '全家福' }],
      related_people_detail: [{ id: 1, name: '李大山' }, { id: 2, name: '王秀兰' }, { id: 3, name: '李建国' }, { id: 4, name: '李建华' }, { id: 5, name: '李建梅' }],
      created_at: '2024-03-05T16:20:00',
      updated_at: '2024-03-06T09:10:00'
    },
    {
      id: 4,
      title: '关于1968年全家福的不同版本',
      content: '我记得当时是二叔参军回来，不是从北大荒回来。而且拍照地点是在沈阳，不是青岛老家。',
      occur_year: 1968,
      occur_place: '辽宁沈阳',
      author: '二叔本人',
      status: 'conflicted',
      related_photos_count: 1,
      related_people_count: 3,
      related_photos_detail: [{ id: 2, title: '1968年春节全家福', era_display: '1960年代', scene_display: '全家福' }],
      related_people_detail: [{ id: 4, name: '李建华' }],
      created_at: '2024-03-06T11:00:00',
      updated_at: '2024-03-06T11:00:00'
    },
    {
      id: 5,
      title: '妈妈在纺织厂当标兵的那些年',
      content: '妈妈1975年进天津纺织厂当检验员，因为眼力好、手又快，连续三年评上三八红旗手。她说最忙的时候，一个班要检验八千多个线锭，眼睛经常熬得通红。有一次厂里选她去北京参加表彰大会，她激动得一晚上没睡着，回来还给我们每个人都带了北京果脯。',
      occur_year: 1978,
      occur_place: '天津纺织厂',
      author: '长孙回忆',
      status: 'draft',
      related_photos_count: 1,
      related_people_count: 1,
      related_photos_detail: [{ id: 3, title: '母亲年轻时的工作照', era_display: '1970年代', scene_display: '工作/求学' }],
      related_people_detail: [{ id: 6, name: '张桂芬' }],
      created_at: '2024-03-08T20:00:00',
      updated_at: '2024-03-08T20:00:00'
    },
    {
      id: 6,
      title: '大哥1985年的婚礼',
      content: '大哥结婚那年，家里还是四合院，酒席就摆在院子里，请了村东头的王厨子。大姐记得，迎亲的队伍骑着8辆永久牌自行车，新娘穿的红棉袄是妈妈亲手缝的，领口还绣了一朵大牡丹。洞房里点着两根红烛，晚辈们闹洞房闹到后半夜，爷爷笑得合不拢嘴。',
      occur_year: 1985,
      occur_place: '老家四合院',
      author: '三妹回忆',
      status: 'published',
      related_photos_count: 1,
      related_people_count: 10,
      related_photos_detail: [{ id: 4, title: '1985年大哥结婚', era_display: '1980年代', scene_display: '婚礼' }],
      related_people_detail: [{ id: 3, name: '李建国' }, { id: 6, name: '张桂芬' }],
      created_at: '2024-02-14T13:30:00',
      updated_at: '2024-02-18T17:45:00'
    }
  ]
}

function enrichMemory(m) {
  const full = mockMemories().find(x => x.id === m.id)
  return full || { ...m, related_photos_detail: [], related_people_detail: [] }
}

function mockAllMemoryTasks() {
  return [
    { id: 301, task_type: 'event_narration', title: '补充闯关东路上的更多细节', status: 'in_progress', source_type: 'memory', related_memory: 1, created_at: '2024-03-10' },
    { id: 302, task_type: 'relation_verify', title: '核实同行的同乡人物关系', status: 'open', source_type: 'memory', related_memory: 1, created_at: '2024-03-09' },
    { id: 303, task_type: 'event_narration', title: '补充北大荒冬天抢收粮食的故事', status: 'submitted', source_type: 'memory', related_memory: 2, created_at: '2024-03-08' },
    { id: 304, task_type: 'identity_confirm', title: '确认冲突版本中的拍照地点', status: 'conflicted', source_type: 'memory', related_memory: 4, created_at: '2024-03-07' },
    { id: 305, task_type: 'event_narration', title: '核对1968年全家福的人物身份', status: 'completed', source_type: 'memory', related_memory: 3, created_at: '2024-03-01' }
  ]
}
</script>

<style scoped>
.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.status-stat-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.status-stat {
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  text-align: center;
}

.status-stat.active {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.status-stat.draft {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #1E40AF;
}
.status-stat.draft.active { border-color: #3B82F6; }

.status-stat.submitted {
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  color: #92400E;
}
.status-stat.submitted.active { border-color: #F59E0B; }

.status-stat.published {
  background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
  color: #065F46;
}
.status-stat.published.active { border-color: #10B981; }

.status-stat.conflicted {
  background: linear-gradient(135deg, #FEF2F2, #FEE2E2);
  color: #991B1B;
}
.status-stat.conflicted.active { border-color: #EF4444; }

.status-stat.all {
  background: linear-gradient(135deg, #F5F0E6, #E8D8C4);
  color: #8B4513;
}
.status-stat.all.active { border-color: #8B4513; }

.stat-num {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
}

.memories-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.memory-card {
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.memory-card:hover {
  transform: translateX(4px);
  box-shadow: 0 6px 18px rgba(139, 69, 19, 0.1);
}

.memory-header {
  margin-bottom: 12px;
}

.memory-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.memory-title {
  font-size: 18px;
  font-weight: 600;
  color: #8B4513;
}

.memory-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 13px;
  color: #8B7355;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.memory-content-preview {
  color: #5D4E3A;
  line-height: 1.8;
  font-size: 14px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #FFFAF0;
  border-left: 3px solid #D4A574;
  border-radius: 0 8px 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.memory-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-top: 14px;
  border-top: 1px solid #F5EDE0;
  flex-wrap: wrap;
  gap: 12px;
}

.linked-assets {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  flex: 1;
}

.linked-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: #8B7355;
}

.linked-photos, .linked-persons {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.linked-photo-thumb {
  width: 36px;
  height: 36px;
  background: #F5EDE0;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.more-count {
  font-size: 12px;
  color: #8B4513;
  font-weight: 600;
  align-self: center;
}

.memory-actions {
  display: flex;
  gap: 8px;
}

.memory-detail {
  padding: 8px 0;
}

.detail-meta-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.detail-content-text {
  font-size: 15px;
  line-height: 2;
  color: #3D2914;
  padding: 20px;
  background: linear-gradient(135deg, #FFFAF0, #FFF8F0);
  border-radius: 12px;
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.detail-link-section {
  margin-bottom: 20px;
}

.detail-link-section h4 {
  font-size: 15px;
  font-weight: 600;
  color: #8B4513;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
}

.detail-photo {
  background: #FFFAF0;
  border: 1px solid #E8D8C4;
  border-radius: 8px;
  padding: 10px;
}

.dp-thumb {
  height: 90px;
  background: linear-gradient(135deg, #F5F0E6, #E8D8C4);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  margin-bottom: 8px;
}

.dp-title {
  font-size: 13px;
  font-weight: 600;
  color: #5D4E3A;
  margin-bottom: 2px;
}

.dp-meta {
  font-size: 11px;
  color: #B5A48C;
}

.detail-person-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-time {
  padding-top: 16px;
  border-top: 1px solid #F5EDE0;
  font-size: 12px;
  color: #B5A48C;
  text-align: right;
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-actions {
  display: flex;
  gap: 8px;
}

.detail-task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.detail-task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #F0E6D6;
  cursor: pointer;
  transition: all 0.2s;
}

.detail-task-item:hover {
  background: #FFF5E6;
  border-color: #D4A574;
}

.dti-title {
  flex: 1;
  font-size: 14px;
  color: #5D4E3A;
}

.task-detail-section {
  background: linear-gradient(135deg, #FFF8F0, #FFFAF0);
  border: 1px solid #F4A460;
  border-radius: 12px;
}
</style>
