<template>
  <div class="confirm-page">
    <div class="page-header">
      <div class="page-title">
        <el-icon><CircleCheck /></el-icon>
        家庭确认台
      </div>
      <div class="page-subtitle">当补注信息有冲突时，家庭成员共同投票确认，用共识守护家族记忆的真实性</div>
    </div>

    <div class="conflicts-section" style="margin-bottom: 28px;">
      <div class="section-header">
        <h2 class="section-heading">
          <el-icon style="color: #EF4444;"><Warning /></el-icon>
          冲突版本
          <el-tag type="danger" effect="light">{{ openConflicts.length }} 条待处理</el-tag>
        </h2>
        <el-button type="primary" class="btn-primary-warm" size="small" @click="showAddConflict = true">
          <el-icon><Plus /></el-icon>登记冲突
        </el-button>
      </div>

      <div v-if="!openConflicts.length" class="card-warm empty-warm">
        <el-icon :size="48" style="color: #10B981; margin-bottom: 12px;"><CircleCheckFilled /></el-icon>
        <div>暂无可处理的冲突版本</div>
      </div>

      <div v-else class="conflict-list">
        <div v-for="c in openConflicts" :key="c.id" class="conflict-card card-warm">
          <div class="conflict-header">
            <div class="conflict-title-row">
              <h3>{{ c.description || `${c.conflict_field_display} 冲突` }}</h3>
              <el-tag type="danger" effect="light">待确认</el-tag>
            </div>
            <div class="conflict-meta">
              <el-tag size="small" type="warning">{{ c.conflict_field_display }}</el-tag>
              <span v-if="c.related_person_name">👤 {{ c.related_person_name }}</span>
              <span v-if="c.related_photo_title">📷 {{ c.related_photo_title }}</span>
              <span v-if="c.related_memory_title">📜 {{ c.related_memory_title }}</span>
              <span class="meta-time"><el-icon><Clock /></el-icon> {{ formatDate(c.created_at) }}</span>
            </div>
          </div>
          <div class="conflict-versions">
            <div class="version-card version-a">
              <div class="version-label">
                <span class="version-badge a">A</span>
                <span>原版本 · 提交人：{{ c.version_a_author || '初始记录' }}</span>
              </div>
              <div class="version-content">{{ c.version_a }}</div>
            </div>
            <div class="version-vs">VS</div>
            <div class="version-card version-b">
              <div class="version-label">
                <span class="version-badge b">B</span>
                <span>新版本 · 提交人：{{ c.version_b_author || '补注家属' }}</span>
              </div>
              <div class="version-content">{{ c.version_b }}</div>
            </div>
          </div>
          <div class="conflict-actions">
            <span class="action-hint">请家庭成员投票确认正确版本：</span>
            <div style="flex: 1"></div>
            <el-button type="success" @click="resolveConflict(c, 'A')">
              <el-icon><Check /></el-icon>确认版本A
            </el-button>
            <el-button type="primary" class="btn-primary-warm" @click="resolveConflict(c, 'B')">
              <el-icon><Check /></el-icon>确认版本B
            </el-button>
            <el-button @click="createConfirmation(c)">
              <el-icon><Stamp /></el-icon>发起家庭投票
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="confirm-section">
      <div class="section-header">
        <h2 class="section-heading">
          <el-icon style="color: #F59E0B;"><Stamp /></el-icon>
          家庭确认事项
          <el-tag type="warning" effect="light">{{ pendingConfirmations.length }} 项投票中</el-tag>
        </h2>
        <el-button type="primary" class="btn-primary-warm" size="small" @click="showAddConfirm = true">
          <el-icon><Plus /></el-icon>发起确认
        </el-button>
      </div>

      <div class="filter-bar card-warm" style="padding: 14px 20px; margin-bottom: 16px;">
        <span style="font-size: 13px; color: #8B7355;">筛选：</span>
        <el-radio-group v-model="confirmFilter" size="small">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="pending">待投票</el-radio-button>
          <el-radio-button label="approved">已通过</el-radio-button>
          <el-radio-button label="rejected">已否决</el-radio-button>
          <el-radio-button label="tied">平票待议</el-radio-button>
        </el-radio-group>
        <div style="flex: 1"></div>
        <el-select v-model="confirmTypeFilter" placeholder="按类型" size="small" clearable style="width: 140px;">
          <el-option v-for="t in CONFIRM_TYPE_OPTIONS" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>

      <div v-if="!filteredConfirmations.length" class="card-warm empty-warm">
        <el-icon :size="48" style="color: #D4A574; margin-bottom: 12px;"><DocumentAdd /></el-icon>
        <div>暂无确认事项</div>
      </div>

      <div v-else class="confirm-list">
        <div v-for="item in filteredConfirmations" :key="item.id" class="confirm-card card-warm">
          <div class="confirm-header">
            <div class="confirm-type-badge" :class="item.confirm_type">
              {{ item.confirm_type_display }}
            </div>
            <h3>{{ item.title }}</h3>
            <el-tag
              size="small"
              :type="getConfirmStatusType(item.status)"
              effect="light"
              style="margin-left: auto;"
            >
              {{ item.status_display }}
            </el-tag>
          </div>
          <div class="confirm-meta">
            <span>提案人：{{ item.proposer }}</span>
            <span><el-icon><Clock /></el-icon> {{ formatDate(item.created_at) }}</span>
            <span v-if="item.deadline" class="deadline">
              <el-icon><Timer /></el-icon> 截止：{{ formatDate(item.deadline) }}
            </span>
          </div>
          <div class="confirm-detail">
            {{ item.detail }}
          </div>
          <div class="confirm-vote-section" v-if="item.status === 'pending' || item.status === 'tied'">
            <div class="vote-results">
              <div class="vote-bar approve">
                <div class="bar-inner" :style="{ width: getApprovePct(item) + '%' }"></div>
                <span class="bar-label">赞成 {{ item.vote_approve }}</span>
              </div>
              <div class="vote-bar reject">
                <div class="bar-inner" :style="{ width: getRejectPct(item) + '%' }"></div>
                <span class="bar-label">反对 {{ item.vote_reject }}</span>
              </div>
            </div>
            <div class="vote-actions">
              <span class="vote-hint">您的投票：</span>
              <el-button type="success" size="small" @click="vote(item, 'approve')">
                <el-icon><CircleCheckFilled /></el-icon>赞成
              </el-button>
              <el-button type="danger" size="small" @click="vote(item, 'reject')">
                <el-icon><CircleCloseFilled /></el-icon>反对
              </el-button>
              <span style="font-size: 12px; color: #B5A48C; margin-left: 8px;">
                已投票：{{ (item.voters || []).join('、') || '暂无' }}
              </span>
            </div>
          </div>
          <div v-else class="confirm-result">
            <div class="result-stat approve"><el-icon><CircleCheckFilled /></el-icon> 赞成：{{ item.vote_approve }}票</div>
            <div class="result-stat reject"><el-icon><CircleCloseFilled /></el-icon> 反对：{{ item.vote_reject }}票</div>
            <el-tag
              size="large"
              :type="getConfirmStatusType(item.status)"
              style="margin-left: auto;"
            >
              {{ item.status === 'approved' ? '✅ 家庭共识通过' : item.status === 'rejected' ? '❌ 共识不通过' : '⚖️ 平票需复议' }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAddConflict" title="登记信息冲突" width="600px">
      <el-form :model="conflictForm" label-width="110px">
        <el-form-item label="冲突类型" required>
          <el-select v-model="conflictForm.conflict_field" style="width: 100%">
            <el-option v-for="f in CONFLICT_FIELD_OPTIONS" :key="f.value" :label="f.label" :value="f.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联人物">
          <el-select v-model="conflictForm.related_person" filterable clearable style="width: 100%" placeholder="选填">
            <el-option v-for="p in allPersons" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联照片">
          <el-select v-model="conflictForm.related_photo" filterable clearable style="width: 100%" placeholder="选填">
            <el-option v-for="p in allPhotos" :key="p.id" :label="p.title || `照片#${p.id}`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="原版本（A）" required>
          <el-input v-model="conflictForm.version_a" type="textarea" :rows="3" placeholder="原始记录内容" />
        </el-form-item>
        <el-form-item label="版本A提交人">
          <el-input v-model="conflictForm.version_a_author" />
        </el-form-item>
        <el-form-item label="新版本（B）" required>
          <el-input v-model="conflictForm.version_b" type="textarea" :rows="3" placeholder="家属补注的不同内容" />
        </el-form-item>
        <el-form-item label="版本B提交人">
          <el-input v-model="conflictForm.version_b_author" />
        </el-form-item>
        <el-form-item label="冲突说明">
          <el-input v-model="conflictForm.description" type="textarea" :rows="2" placeholder="描述冲突的情况" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddConflict = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitConflict">提交登记</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAddConfirm" title="发起家庭确认" width="600px">
      <el-form :model="confirmForm" label-width="110px">
        <el-form-item label="确认类型" required>
          <el-select v-model="confirmForm.confirm_type" style="width: 100%">
            <el-option v-for="t in CONFIRM_TYPE_OPTIONS" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="确认事项" required>
          <el-input v-model="confirmForm.title" placeholder="如：确认二叔1968年春节是否在沈阳" />
        </el-form-item>
        <el-form-item label="详细内容" required>
          <el-input v-model="confirmForm.detail" type="textarea" :rows="4" placeholder="详细说明需要确认的内容、背景、两种说法等" />
        </el-form-item>
        <el-form-item label="提案人">
          <el-input v-model="confirmForm.proposer" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddConfirm = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitConfirm">发起投票</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  CircleCheck, Warning, Plus, Clock, Check, Stamp, DocumentAdd,
  Timer, CircleCheckFilled, CircleCloseFilled
} from '@element-plus/icons-vue'
import { conflicts, confirmations, photos as photoApi, persons as personApi } from '@/api'
import { CONFIRM_TYPE_OPTIONS, CONFLICT_FIELD_OPTIONS } from '@/store'

const conflictsList = ref([])
const confirmationsList = ref([])
const allPersons = ref([])
const allPhotos = ref([])
const confirmFilter = ref('')
const confirmTypeFilter = ref('')
const showAddConflict = ref(false)
const showAddConfirm = ref(false)
const currentVoter = ref('长孙')

const conflictForm = ref({
  conflict_field: 'other', related_person: null, related_photo: null,
  version_a: '', version_a_author: '', version_b: '', version_b_author: '', description: ''
})
const confirmForm = ref({
  confirm_type: 'person', title: '', detail: '', proposer: '家属'
})

const openConflicts = computed(() => conflictsList.value.filter(c => c.status === 'open'))
const pendingConfirmations = computed(() => confirmationsList.value.filter(c => c.status === 'pending'))

const filteredConfirmations = computed(() => {
  let r = confirmationsList.value
  if (confirmFilter.value) r = r.filter(c => c.status === confirmFilter.value)
  if (confirmTypeFilter.value) r = r.filter(c => c.confirm_type === confirmTypeFilter.value)
  return r
})

const formatDate = (d) => {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`
}

const getConfirmStatusType = (s) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger', tied: 'info' }
  return map[s] || 'info'
}

const getApprovePct = (item) => {
  const total = item.vote_approve + item.vote_reject
  if (total === 0) return 0
  return Math.round((item.vote_approve / Math.max(total, 3)) * 100)
}
const getRejectPct = (item) => {
  const total = item.vote_approve + item.vote_reject
  if (total === 0) return 0
  return Math.round((item.vote_reject / Math.max(total, 3)) * 100)
}

const loadData = async () => {
  try {
    const [cRes, confRes, pRes, photoRes] = await Promise.all([
      conflicts.list({ page_size: 100 }).catch(() => ({ results: mockConflicts() })),
      confirmations.list({ page_size: 100 }).catch(() => ({ results: mockConfirmations() })),
      personApi.simple().catch(() => []),
      photoApi.simple().catch(() => [])
    ])
    conflictsList.value = cRes.results || cRes || mockConflicts()
    confirmationsList.value = confRes.results || confRes || mockConfirmations()
    allPersons.value = pRes.results || pRes || []
    allPhotos.value = photoRes.results || photoRes || []
  } catch (e) {
    conflictsList.value = mockConflicts()
    confirmationsList.value = mockConfirmations()
  }
}

const resolveConflict = async (c, version) => {
  try {
    await conflicts.resolve(c.id, version, currentVoter.value)
    ElMessage.success(`已确认版本${version}`)
  } catch (e) {
    const target = conflictsList.value.find(x => x.id === c.id)
    if (target) {
      target.status = 'resolved'
      target.resolved_version = version
    }
    ElMessage.success(`已确认版本${version}（模拟）`)
  }
  loadData()
}

const createConfirmation = (c) => {
  confirmForm.value = {
    confirm_type: 'conflict',
    title: `关于【${c.conflict_field_display}】的家庭确认`,
    detail: `版本A：${c.version_a}\n\n版本B：${c.version_b}\n\n请各位家属投票确认正确版本。`,
    proposer: currentVoter.value
  }
  showAddConfirm.value = true
}

const vote = async (item, voteType) => {
  if ((item.voters || []).includes(currentVoter.value)) {
    ElMessage.warning('您已投过票')
    return
  }
  try {
    await confirmations.vote(item.id, currentVoter.value, voteType)
    ElMessage.success('投票成功')
  } catch (e) {
    const target = confirmationsList.value.find(x => x.id === item.id)
    if (target) {
      if (voteType === 'approve') target.vote_approve++
      else target.vote_reject++
      if (!target.voters) target.voters = []
      target.voters.push(currentVoter.value)
      const total = target.vote_approve + target.vote_reject
      if (total >= 3) {
        if (target.vote_approve > target.vote_reject) target.status = 'approved'
        else if (target.vote_reject > target.vote_approve) target.status = 'rejected'
        else target.status = 'tied'
      }
    }
    ElMessage.success('投票成功（模拟）')
  }
  loadData()
}

const submitConflict = async () => {
  if (!conflictForm.value.version_a || !conflictForm.value.version_b) {
    ElMessage.warning('请填写两个版本的内容')
    return
  }
  try {
    await conflicts.create({ ...conflictForm.value, status: 'open' })
    ElMessage.success('冲突已登记')
  } catch (e) {
    conflictsList.value.unshift({
      id: Date.now(), ...conflictForm.value, status: 'open',
      conflict_field_display: CONFLICT_FIELD_OPTIONS.find(x => x.value === conflictForm.value.conflict_field)?.label,
      created_at: new Date().toISOString()
    })
    ElMessage.success('冲突已登记（模拟）')
  }
  showAddConflict.value = false
  conflictForm.value = { conflict_field: 'other', related_person: null, related_photo: null, version_a: '', version_a_author: '', version_b: '', version_b_author: '', description: '' }
  loadData()
}

const submitConfirm = async () => {
  if (!confirmForm.value.title || !confirmForm.value.detail) {
    ElMessage.warning('请完善确认信息')
    return
  }
  try {
    await confirmations.create({ ...confirmForm.value, status: 'pending', vote_approve: 0, vote_reject: 0, voters: [] })
    ElMessage.success('确认已发起')
  } catch (e) {
    confirmationsList.value.unshift({
      id: Date.now(), ...confirmForm.value, status: 'pending',
      confirm_type_display: CONFIRM_TYPE_OPTIONS.find(x => x.value === confirmForm.value.confirm_type)?.label,
      status_display: '待投票',
      vote_approve: 0, vote_reject: 0, voters: [],
      created_at: new Date().toISOString()
    })
    ElMessage.success('确认已发起（模拟）')
  }
  showAddConfirm.value = false
  confirmForm.value = { confirm_type: 'person', title: '', detail: '', proposer: '家属' }
  loadData()
}

onMounted(loadData)
</script>

<script>
function mockConflicts() {
  return [
    {
      id: 1,
      conflict_field: 'photo_date',
      conflict_field_display: '拍摄时间',
      related_person: null,
      related_person_name: null,
      related_photo: 2,
      related_photo_title: '1968年春节全家福',
      related_memory: null,
      related_memory_title: null,
      version_a: '1968年春节，大年初三拍摄',
      version_a_author: '大姑回忆',
      version_b: '1969年春节，二叔请假从北大荒回来那次',
      version_b_author: '二叔本人',
      description: '关于这张全家福的拍摄年份，大姑和二叔的记忆有出入。需要确认二叔从北大荒第一次回家探亲的确切年份。',
      status: 'open',
      created_at: '2024-03-06T11:30:00'
    },
    {
      id: 2,
      conflict_field: 'person_relation',
      conflict_field_display: '亲属关系',
      related_person: 8,
      related_person_name: '未知老人',
      related_photo: null,
      related_photo_title: null,
      related_memory: null,
      related_memory_title: null,
      version_a: '这是李大山的亲弟弟，叫李大河',
      version_a_author: '三姑听奶奶说的',
      version_b: '这是李大山的表哥，从山东来投奔的，住了半年就走了',
      version_b_author: '二叔听爷爷提过一次',
      description: '老照片夹层中发现的照片，背面字迹模糊，疑似家中长辈。关于此人身份有两种说法。',
      status: 'open',
      created_at: '2024-03-07T15:20:00'
    },
    {
      id: 3,
      conflict_field: 'photo_location',
      conflict_field_display: '拍摄地点',
      related_person: null,
      related_person_name: null,
      related_photo: 9,
      related_photo_title: '奶奶少女时代',
      related_memory: null,
      related_memory_title: null,
      version_a: '南京外婆家门口',
      version_a_author: '奶奶生前说过',
      version_b: '南京女子中学门口',
      version_b_author: '大姑看照片上的校服',
      status: 'open',
      description: '',
      created_at: '2024-03-08T09:15:00'
    }
  ]
}

function mockConfirmations() {
  return [
    {
      id: 101,
      confirm_type: 'conflict',
      confirm_type_display: '冲突版本',
      title: '确认1968年全家福的拍摄年份',
      detail: '版本A：1968年春节，大年初三拍摄（大姑回忆）\n\n版本B：1969年春节，二叔请假从北大荒回来那次（二叔本人）\n\n请各位家属结合照片中人物衣着、二叔返乡时间综合判断。',
      proposer: '长孙',
      status: 'pending',
      vote_approve: 2,
      vote_reject: 1,
      voters: ['大姑', '三妹', '二叔'],
      created_at: '2024-03-06T14:00:00'
    },
    {
      id: 102,
      confirm_type: 'person',
      confirm_type_display: '人物信息',
      title: '确认"未知老人"的身份',
      detail: '老照片夹层中发现的照片，背面有模糊字迹"大河边"。\n\n说法一：李大山的亲弟弟李大河\n说法二：李大山的表哥，从山东来投奔。\n\n请老一辈家属回忆并确认。',
      proposer: '长孙媳',
      status: 'pending',
      vote_approve: 1,
      vote_reject: 2,
      voters: ['三姑', '二叔', '大姑'],
      created_at: '2024-03-07T16:30:00'
    },
    {
      id: 103,
      confirm_type: 'memory',
      confirm_type_display: '回忆内容',
      title: '确认闯关东的出发年份',
      detail: '关于爷爷闯关东的年份：\n\n说法一：1934年，爷爷19岁（长孙笔记）\n说法二：1936年，爷爷21岁（三姑印象）\n\n需要统一写入家族史。',
      proposer: '长孙',
      status: 'approved',
      vote_approve: 4,
      vote_reject: 0,
      voters: ['二叔', '大姑', '三姑', '大哥'],
      created_at: '2024-02-15T10:00:00'
    },
    {
      id: 104,
      confirm_type: 'photo_person',
      confirm_type_display: '照片人物',
      title: '确认1985年婚礼照片中"后排左三"是谁',
      detail: '1985年大哥婚礼照片，后排左三的年轻人身份存疑。\n\n说法一：新娘的表弟\n说法二：新郎的发小\n\n请当年在场的家属确认。',
      proposer: '三妹',
      status: 'tied',
      vote_approve: 1,
      vote_reject: 1,
      voters: ['大嫂', '三妹'],
      created_at: '2024-03-01T18:00:00'
    },
    {
      id: 105,
      confirm_type: 'relation',
      confirm_type_display: '亲属关系',
      title: '确认张桂芬与李建国的关系为"配偶"',
      detail: '经晚辈整理，确认张桂芬（天津人，1958年生）为李建国的配偶，1980年结婚。请确认。',
      proposer: '长孙媳整理',
      status: 'approved',
      vote_approve: 5,
      vote_reject: 0,
      voters: ['李建国', '张桂芬', '大姑', '二叔', '三姑'],
      created_at: '2024-01-20T11:00:00'
    }
  ]
}
</script>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #E8D8C4;
}

.section-heading {
  font-size: 18px;
  font-weight: 600;
  color: #8B4513;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 16px;
}

.section-header .el-button {
  margin-left: auto;
}

.conflict-list, .confirm-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.conflict-card {
  padding: 20px;
  border-left: 4px solid #EF4444;
}

.conflict-header {
  margin-bottom: 16px;
}

.conflict-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.conflict-title-row h3 {
  font-size: 16px;
  font-weight: 600;
  color: #3D2914;
}

.conflict-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 13px;
  color: #8B7355;
  align-items: center;
}

.meta-time {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}

.conflict-versions {
  display: grid;
  grid-template-columns: 1fr 40px 1fr;
  gap: 12px;
  margin-bottom: 20px;
  align-items: stretch;
}

.version-card {
  padding: 14px 16px;
  border-radius: 10px;
  position: relative;
}

.version-a {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border: 1px solid #93C5FD;
}

.version-b {
  background: linear-gradient(135deg, #FEF3C7, #FDE68A);
  border: 1px solid #FBBF24;
}

.version-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #5D4E3A;
  margin-bottom: 8px;
  font-weight: 500;
}

.version-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 13px;
}

.version-badge.a {
  background: #3B82F6;
}

.version-badge.b {
  background: #D97706;
}

.version-content {
  font-size: 14px;
  line-height: 1.7;
  color: #3D2914;
}

.version-vs {
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #D2691E;
  font-size: 16px;
  background: #FEF3E2;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  align-self: center;
  justify-self: center;
}

.conflict-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px dashed #E8D8C4;
}

.action-hint {
  font-size: 13px;
  color: #8B7355;
}

.confirm-card {
  padding: 20px;
  border-left: 4px solid #F59E0B;
}

.confirm-card.approved { border-left-color: #10B981; }
.confirm-card.rejected { border-left-color: #EF4444; }
.confirm-card.tied { border-left-color: #6366F1; }

.confirm-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.confirm-type-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.confirm-type-badge.person { background: #8B5CF6; }
.confirm-type-badge.relation { background: #EC4899; }
.confirm-type-badge.photo_info { background: #3B82F6; }
.confirm-type-badge.photo_person { background: #14B8A6; }
.confirm-type-badge.memory { background: #F59E0B; }
.confirm-type-badge.conflict { background: #EF4444; }

.confirm-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #3D2914;
}

.confirm-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #8B7355;
  margin-bottom: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.deadline {
  color: #DC2626;
  font-weight: 500;
}

.confirm-detail {
  padding: 12px 16px;
  background: #FFFAF0;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.8;
  color: #5D4E3A;
  margin-bottom: 16px;
  white-space: pre-wrap;
}

.confirm-vote-section {
  padding-top: 16px;
  border-top: 1px dashed #E8D8C4;
}

.vote-results {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}

.vote-bar {
  height: 28px;
  border-radius: 14px;
  position: relative;
  overflow: hidden;
}

.vote-bar.approve {
  background: #D1FAE5;
}
.vote-bar.reject {
  background: #FEE2E2;
}

.bar-inner {
  height: 100%;
  border-radius: 14px;
  transition: width 0.3s;
}

.vote-bar.approve .bar-inner {
  background: linear-gradient(90deg, #10B981, #059669);
}
.vote-bar.reject .bar-inner {
  background: linear-gradient(90deg, #EF4444, #DC2626);
}

.bar-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: 600;
  color: #1F2937;
}

.vote-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.vote-hint {
  font-size: 13px;
  color: #8B7355;
  margin-right: 4px;
}

.confirm-result {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px dashed #E8D8C4;
}

.result-stat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
}

.result-stat.approve { color: #059669; }
.result-stat.reject { color: #DC2626; }

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
