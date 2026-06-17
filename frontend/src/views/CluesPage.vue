<template>
  <div class="clues-page">
    <div class="page-header">
      <div class="page-title">
        <el-icon><Search /></el-icon>
        人物线索管理
      </div>
      <div class="page-subtitle">聚合照片标注中暂用名/待确认人物线索，统一认领归档到人物档案</div>
    </div>

    <div class="stats-bar card-warm">
      <div class="stat-item">
        <div class="stat-num">{{ clueStats.total_clues || 0 }}</div>
        <div class="stat-label">待认领线索</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">{{ clueStats.unconfirmed_annotations || 0 }}</div>
        <div class="stat-label">未确认标注</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">{{ clueStats.multi_photo_clues || 0 }}</div>
        <div class="stat-label">跨照片线索</div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-num">{{ clueStats.single_photo_clues || 0 }}</div>
        <div class="stat-label">单照片线索</div>
      </div>
    </div>

    <div class="content-layout">
      <div class="list-panel card-warm">
        <div class="panel-header">
          <el-input v-model="searchText" placeholder="搜索线索名称/位置/照片..." size="default" clearable @keyup.enter="loadClues">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button type="primary" class="btn-primary-warm" @click="loadClues">
            <el-icon><Search /></el-icon>搜索
          </el-button>
        </div>

        <div class="filter-bar">
          <el-radio-group v-model="filterMode" size="small">
            <el-radio-button value="all">全部线索</el-radio-button>
            <el-radio-button value="multi">多照片线索</el-radio-button>
            <el-radio-button value="single">单照片线索</el-radio-button>
          </el-radio-group>
          <el-select v-model="sortBy" size="small" style="width: 140px;" @change="loadClues">
            <el-option label="按数量降序" value="count_desc" />
            <el-option label="按数量升序" value="count_asc" />
            <el-option label="按名称排序" value="name_asc" />
            <el-option label="按最近出现" value="last_seen_desc" />
          </el-select>
        </div>

        <div class="batch-bar" v-if="selectedClues.length > 0">
          <el-tag type="warning">已选 {{ selectedClues.length }} 条线索</el-tag>
          <el-button size="small" type="primary" class="btn-primary-warm" @click="openBatchClaim">
            <el-icon><User /></el-icon>批量认领
          </el-button>
          <el-button size="small" @click="clearSelection">取消选择</el-button>
        </div>

        <div class="clue-list" v-loading="loading">
          <div
            v-for="clue in clueList"
            :key="clue.clue_key"
            class="clue-card"
            :class="{ active: currentClue?.clue_key === clue.clue_key, selected: selectedClues.includes(clue.clue_key) }"
            @click="selectClue(clue)"
          >
            <div class="clue-checkbox" @click.stop="toggleSelect(clue.clue_key)">
              <el-checkbox :model-value="selectedClues.includes(clue.clue_key)" />
            </div>
            <div class="clue-avatar">
              <el-avatar :size="48" style="background: linear-gradient(135deg, #F59E0B, #D97706);">
                {{ clue.clue_name?.charAt(0) || '?' }}
              </el-avatar>
            </div>
            <div class="clue-info">
              <div class="clue-name">
                {{ clue.clue_name }}
                <el-tag size="small" type="warning" effect="light">
                  {{ clue.count }} 张照片
                </el-tag>
              </div>
              <div class="clue-meta">
                <span v-if="clue.position_notes?.length" class="meta-item">
                  📍 {{ clue.position_notes.slice(0, 2).join('、') }}
                </span>
                <span v-if="clue.old_titles?.length" class="meta-item">
                  👋 {{ clue.old_titles.slice(0, 1).join('、') }}
                </span>
              </div>
              <div class="clue-time">
                首次出现：{{ formatDate(clue.first_seen) }}
              </div>
            </div>
            <div class="clue-action">
              <el-button size="small" type="primary" class="btn-primary-warm" @click.stop="openClaim(clue)">
                认领
              </el-button>
            </div>
          </div>
          <el-empty v-if="!clueList.length && !loading" description="暂无待认领线索" />
        </div>

        <div class="pagination" v-if="totalCount > pageSize">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalCount"
            layout="prev, pager, next"
            @current-change="loadClues"
          />
        </div>
      </div>

      <div class="detail-panel card-warm">
        <div v-if="!currentClue" class="empty-detail">
          <el-icon :size="64" style="color: #D4A574; margin-bottom: 16px;"><Search /></el-icon>
          <div class="empty-title">从左侧选择一条线索</div>
          <div class="empty-desc">查看线索详情、关联照片，进行认领操作</div>
        </div>
        <div v-else class="clue-detail">
          <div class="detail-header">
            <div class="avatar-section">
              <el-avatar :size="72" style="background: linear-gradient(135deg, #F59E0B, #D97706);">
                {{ currentClue.clue_name?.charAt(0) || '?' }}
              </el-avatar>
            </div>
            <div class="info-section">
              <h2 class="detail-name">{{ currentClue.clue_name }}</h2>
              <div class="detail-tags">
                <el-tag type="warning">{{ currentClue.count }} 张照片</el-tag>
                <el-tag v-if="currentClue.count > 1" type="danger">跨照片线索</el-tag>
                <el-tag v-else effect="plain">单照片线索</el-tag>
              </div>
              <div class="detail-meta">
                <div class="meta-row">
                  <span class="meta-label">首次出现：</span>
                  <span>{{ formatDate(currentClue.first_seen) }}</span>
                </div>
                <div class="meta-row">
                  <span class="meta-label">最近出现：</span>
                  <span>{{ formatDate(currentClue.last_seen) }}</span>
                </div>
              </div>
              <div class="detail-actions">
                <el-button type="primary" class="btn-primary-warm" @click="openClaim(currentClue)">
                  <el-icon><User /></el-icon>认领此线索
                </el-button>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3 class="section-title">位置说明</h3>
            <div class="tag-list" v-if="currentClue.position_notes?.length">
              <el-tag v-for="(pos, idx) in currentClue.position_notes" :key="idx" effect="plain">
                📍 {{ pos }}
              </el-tag>
            </div>
            <el-empty v-else description="暂无位置说明" :image-size="80" />
          </div>

          <div class="detail-section">
            <h3 class="section-title">旧时称呼</h3>
            <div class="tag-list" v-if="currentClue.old_titles?.length">
              <el-tag v-for="(title, idx) in currentClue.old_titles" :key="idx" effect="plain">
                👋 {{ title }}
              </el-tag>
            </div>
            <el-empty v-else description="暂无旧时称呼" :image-size="80" />
          </div>

          <div class="detail-section">
            <h3 class="section-title">关联照片 ({{ currentClue.items?.length || 0 }})</h3>
            <div class="photo-grid">
              <div
                v-for="item in currentClue.items"
                :key="item.id"
                class="photo-item"
              >
                <div class="photo-thumb">
                  <img :src="getImageSrc(item.photo_detail)" v-if="item.photo_detail?.image_url" />
                  <span class="photo-emoji" v-else>{{ photoPlaceholder(item.photo_detail?.era, item.photo_detail?.scene) }}</span>
                </div>
                <div class="photo-info">
                  <div class="photo-title">{{ item.photo_detail?.title || '未命名照片' }}</div>
                  <div class="photo-meta">
                    <span v-if="item.position_note" class="meta-tag">📍 {{ item.position_note }}</span>
                    <span v-if="item.old_title" class="meta-tag">👋 {{ item.old_title }}</span>
                  </div>
                  <div class="photo-footer">
                    <span v-if="item.photo_detail?.era">{{ getOptionLabel(ERA_OPTIONS, item.photo_detail.era) }}</span>
                    <span v-if="item.photo_detail?.taken_year"> · {{ item.photo_detail.taken_year }}年</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="claimDialogVisible" title="认领线索" width="560px" @close="resetClaimForm">
      <div class="claim-dialog">
        <div class="claim-info">
          <el-tag type="warning" size="large">
            共 {{ claimClueCount }} 条线索待认领
          </el-tag>
        </div>

        <el-tabs v-model="claimMode">
          <el-tab-pane label="认领至已有人物" name="existing">
            <div class="claim-form">
              <el-form label-width="100px">
                <el-form-item label="选择人物" required>
                  <el-select
                    v-model="claimForm.person_id"
                    filterable
                    placeholder="搜索并选择人物"
                    style="width: 100%;"
                    @change="onPersonSelect"
                  >
                    <el-option
                      v-for="p in personList"
                      :key="p.id"
                      :label="p.name"
                      :value="p.id"
                    >
                      <span style="float: left;">{{ p.name }}</span>
                      <span style="float: right; color: #8492a6; font-size: 13px;">
                        {{ p.gender === 'M' ? '男' : p.gender === 'F' ? '女' : '未知' }}
                        <span v-if="p.birth_year"> · {{ p.birth_year }}年生</span>
                      </span>
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item v-if="selectedPerson" label="人物信息">
                  <div class="selected-person-info">
                    <el-avatar :size="48" :style="{ background: getAvatarBg(selectedPerson) }">
                      {{ selectedPerson.name?.charAt(0) }}
                    </el-avatar>
                    <div class="person-details">
                      <div class="person-name">{{ selectedPerson.name }}</div>
                      <div class="person-desc">
                        <span v-if="selectedPerson.birth_place">{{ selectedPerson.birth_place }}</span>
                        <span v-if="selectedPerson.birth_year"> · {{ selectedPerson.birth_year }}年生</span>
                      </div>
                    </div>
                  </div>
                </el-form-item>
                <el-form-item label="添加为别名">
                  <el-switch v-model="claimForm.add_as_alias" />
                  <span class="form-hint">将线索名称作为别名添加到该人物</span>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <el-tab-pane label="新建人物认领" name="new">
            <div class="claim-form">
              <el-form :model="newPersonForm" label-width="100px">
                <el-form-item label="姓名" required>
                  <el-input v-model="newPersonForm.name" placeholder="如：李建国" />
                </el-form-item>
                <el-form-item label="性别">
                  <el-radio-group v-model="newPersonForm.gender">
                    <el-radio value="M">男</el-radio>
                    <el-radio value="F">女</el-radio>
                    <el-radio value="U">未知</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="出生年份">
                  <el-input-number v-model="newPersonForm.birth_year" :min="1850" :max="2030" />
                </el-form-item>
                <el-form-item label="出生地">
                  <el-input v-model="newPersonForm.birth_place" />
                </el-form-item>
                <el-form-item label="人物简介">
                  <el-input v-model="newPersonForm.description" type="textarea" :rows="3" />
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>

        <el-form label-width="100px">
          <el-form-item label="认领人">
            <el-input v-model="claimForm.claimed_by" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="claimDialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" :loading="claiming" @click="submitClaim">
          确认认领
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search, User
} from '@element-plus/icons-vue'
import { clues as cluesApi, persons as personsApi } from '@/api'
import { ERA_OPTIONS, getOptionLabel, photoPlaceholder, STATUS_OPTIONS } from '@/store'

const loading = ref(false)
const clueList = ref([])
const currentClue = ref(null)
const searchText = ref('')
const filterMode = ref('all')
const sortBy = ref('count_desc')
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const clueStats = ref({})

const selectedClues = ref([])

const claimDialogVisible = ref(false)
const claimMode = ref('existing')
const claiming = ref(false)
const claimForm = ref({
  person_id: null,
  add_as_alias: true,
  claimed_by: '家属'
})
const newPersonForm = ref({
  name: '',
  gender: 'U',
  birth_year: null,
  birth_place: '',
  description: ''
})
const personList = ref([])
const claimClueKeys = ref([])

const claimClueCount = computed(() => claimClueKeys.value.length)

const selectedPerson = computed(() => {
  if (!claimForm.value.person_id) return null
  return personList.value.find(p => p.id === claimForm.value.person_id)
})

const getAvatarBg = (p) => {
  const map = { confirmed: 'linear-gradient(135deg, #10B981, #059669)', pending: 'linear-gradient(135deg, #F59E0B, #D97706)', conflicted: 'linear-gradient(135deg, #EF4444, #DC2626)' }
  return map[p.status] || map.pending
}

const getImageSrc = (photo) => {
  if (!photo) return ''
  if (photo.image_url) return photo.image_url
  if (typeof photo.image === 'string' && photo.image.startsWith('http')) return photo.image
  if (typeof photo.image === 'string' && photo.image.startsWith('/media')) return photo.image
  if (typeof photo.image === 'string') return '/media/' + photo.image
  return ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const loadStats = async () => {
  try {
    const res = await cluesApi.stats()
    clueStats.value = res || {
      total_clues: 0,
      unconfirmed_annotations: 0,
      multi_photo_clues: 0,
      single_photo_clues: 0,
    }
  } catch (e) {
    clueStats.value = {
      total_clues: 0,
      unconfirmed_annotations: 0,
      multi_photo_clues: 0,
      single_photo_clues: 0,
    }
  }
}

const loadClues = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchText.value || undefined,
    }
    if (sortBy.value === 'count_desc') {
      params.sort_by = 'count'
      params.sort_order = 'desc'
    } else if (sortBy.value === 'count_asc') {
      params.sort_by = 'count'
      params.sort_order = 'asc'
    } else if (sortBy.value === 'name_asc') {
      params.sort_by = 'name'
      params.sort_order = 'asc'
    } else if (sortBy.value === 'last_seen_desc') {
      params.sort_by = 'last_seen'
      params.sort_order = 'desc'
    }
    const res = await cluesApi.list(params)
    let results = res.results || []
    if (filterMode.value === 'multi') {
      results = results.filter(c => c.count > 1)
    } else if (filterMode.value === 'single') {
      results = results.filter(c => c.count === 1)
    }
    clueList.value = results
    totalCount.value = res.count || 0
  } catch (e) {
    clueList.value = mockClues()
    totalCount.value = mockClues().length
  } finally {
    loading.value = false
  }
}

const loadPersons = async () => {
  try {
    const res = await personsApi.simple()
    personList.value = res || []
  } catch (e) {
    personList.value = mockPersonsSimple()
  }
}

const selectClue = async (clue) => {
  currentClue.value = clue
  try {
    const detail = await cluesApi.get(clue.clue_key)
    currentClue.value = detail
  } catch (e) {
    currentClue.value = { ...clue, items: mockClueItems(clue.clue_key) }
  }
}

const toggleSelect = (clueKey) => {
  const idx = selectedClues.value.indexOf(clueKey)
  if (idx > -1) {
    selectedClues.value.splice(idx, 1)
  } else {
    selectedClues.value.push(clueKey)
  }
}

const clearSelection = () => {
  selectedClues.value = []
}

const openClaim = (clue) => {
  claimClueKeys.value = [clue.clue_key]
  if (clue.clue_name) {
    newPersonForm.value.name = clue.clue_name
  }
  claimDialogVisible.value = true
}

const openBatchClaim = () => {
  if (!selectedClues.value.length) {
    ElMessage.warning('请先选择要认领的线索')
    return
  }
  claimClueKeys.value = [...selectedClues.value]
  const firstClue = clueList.value.find(c => c.clue_key === selectedClues.value[0])
  if (firstClue && selectedClues.value.length === 1) {
    newPersonForm.value.name = firstClue.clue_name
  } else {
    newPersonForm.value.name = ''
  }
  claimDialogVisible.value = true
}

const onPersonSelect = () => {
}

const resetClaimForm = () => {
  claimForm.value = {
    person_id: null,
    add_as_alias: true,
    claimed_by: '家属'
  }
  newPersonForm.value = {
    name: '',
    gender: 'U',
    birth_year: null,
    birth_place: '',
    description: ''
  }
  claimMode.value = 'existing'
}

const submitClaim = async () => {
  claiming.value = true
  try {
    const data = {
      clue_keys: claimClueKeys.value,
      mode: claimMode.value,
      claimed_by: claimForm.value.claimed_by,
    }
    if (claimMode.value === 'existing') {
      if (!claimForm.value.person_id) {
        ElMessage.warning('请选择要认领的人物')
        claiming.value = false
        return
      }
      data.person_id = claimForm.value.person_id
      data.add_as_alias = claimForm.value.add_as_alias
    } else {
      if (!newPersonForm.value.name) {
        ElMessage.warning('请输入人物姓名')
        claiming.value = false
        return
      }
      data.person_data = { ...newPersonForm.value }
    }

    const res = await cluesApi.claim(data)
    if (res.success) {
      ElMessage.success(res.message || '认领成功')
      claimDialogVisible.value = false
      selectedClues.value = []
      currentClue.value = null
      loadClues()
      loadStats()
    } else {
      ElMessage.error(res.error || '认领失败')
    }
  } catch (e) {
    ElMessage.success('认领成功（模拟）')
    claimDialogVisible.value = false
    selectedClues.value = []
    currentClue.value = null
    loadClues()
    loadStats()
  } finally {
    claiming.value = false
  }
}

watch(filterMode, () => {
  loadClues()
})

onMounted(() => {
  loadStats()
  loadClues()
  loadPersons()
})
</script>

<script>
function mockClues() {
  return [
    {
      clue_key: 'clue1',
      clue_name: '二姑',
      count: 3,
      first_seen: '1968-02-15T00:00:00',
      last_seen: '1985-05-01T00:00:00',
      position_notes: ['前排右一', '后排左二', '中间'],
      old_titles: ['二丫头', '二姑娘']
    },
    {
      clue_key: 'clue2',
      clue_name: '三舅',
      count: 2,
      first_seen: '1975-03-10T00:00:00',
      last_seen: '1992-08-15T00:00:00',
      position_notes: ['后排左一', '右边'],
      old_titles: ['三哥']
    },
    {
      clue_key: 'clue3',
      clue_name: '外婆',
      count: 1,
      first_seen: '1938-06-01T00:00:00',
      last_seen: '1938-06-01T00:00:00',
      position_notes: ['中间坐着的老人'],
      old_titles: ['老太太']
    },
    {
      clue_key: 'clue4',
      clue_name: '小明',
      count: 1,
      first_seen: '1995-10-01T00:00:00',
      last_seen: '1995-10-01T00:00:00',
      position_notes: ['最前面的小孩'],
      old_titles: ['明明']
    }
  ]
}

function mockClueItems(clueKey) {
  const items = {
    clue1: [
      { id: 1, photo: 2, photo_detail: { id: 2, title: '1968年春节全家福', image: null, image_url: null, era: '1960s', taken_year: 1968, scene: 'family_portrait' }, position_note: '前排右一', old_title: '二丫头', role_note: '14岁', added_by: '大姑', created_at: '1968-02-15' },
      { id: 2, photo: 4, photo_detail: { id: 4, title: '1985年大哥结婚', image: null, image_url: null, era: '1980s', taken_year: 1985, scene: 'wedding' }, position_note: '后排左二', old_title: '二姑娘', role_note: '伴娘', added_by: '三妹', created_at: '1985-05-01' },
    ],
    clue2: [
      { id: 3, photo: 6, photo_detail: { id: 6, title: '2005年家族大聚会', image: null, image_url: null, era: '2000s', taken_year: 2005, scene: 'festival' }, position_note: '后排左一', old_title: '三哥', role_note: '', added_by: '长孙媳', created_at: '2005-10-01' },
    ],
    clue3: [
      { id: 4, photo: 9, photo_detail: { id: 9, title: '奶奶少女时代', image: null, image_url: null, era: '1930s', taken_year: 1938, scene: 'daily_life' }, position_note: '中间坐着的老人', old_title: '老太太', role_note: '', added_by: '三姑', created_at: '1938-06-01' },
    ],
    clue4: [
      { id: 5, photo: 7, photo_detail: { id: 7, title: '我小时候和外公', image: null, image_url: null, era: '1990s', taken_year: 1995, scene: 'childhood' }, position_note: '最前面的小孩', old_title: '明明', role_note: '5岁', added_by: '外孙', created_at: '1995-10-01' },
    ]
  }
  return items[clueKey] || []
}

function mockPersonsSimple() {
  return [
    { id: 1, name: '李大山', gender: 'M', status: 'confirmed' },
    { id: 2, name: '王秀兰', gender: 'F', status: 'confirmed' },
    { id: 3, name: '李建国', gender: 'M', status: 'confirmed', birth_year: 1948, birth_place: '辽宁沈阳' },
    { id: 4, name: '李建华', gender: 'M', status: 'confirmed' },
    { id: 5, name: '李建梅', gender: 'F', status: 'pending' },
    { id: 6, name: '张桂芬', gender: 'F', status: 'confirmed' },
    { id: 7, name: '李明', gender: 'M', status: 'pending' },
  ]
}
</script>

<style scoped>
.clues-page {
  min-height: 100%;
}

.stats-bar {
  display: flex;
  align-items: center;
  padding: 20px 28px;
  margin-bottom: 20px;
  border-radius: 12px;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: #8B4513;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #8B7355;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: #E8D8C4;
}

.content-layout {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 20px;
  align-items: start;
}

.list-panel {
  padding: 16px;
  max-height: calc(100vh - 380px);
  overflow-y: auto;
}

.panel-header {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}

.panel-header .el-input { flex: 1; }

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid #F5EDE0;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin-bottom: 12px;
  background: #FEF3C7;
  border-radius: 8px;
  border: 1px solid #FDE68A;
}

.clue-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.clue-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid #E8D8C4;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background: #FFFAF0;
  align-items: center;
}

.clue-card:hover {
  background: #FFF5E6;
  border-color: #D4A574;
}

.clue-card.active {
  background: linear-gradient(135deg, #FEF3E2, #FFE4C4);
  border-color: #D2691E;
  box-shadow: 0 2px 10px rgba(210, 105, 30, 0.15);
}

.clue-card.selected {
  border-color: #F59E0B;
  background: #FFFBEB;
}

.clue-checkbox {
  flex-shrink: 0;
}

.clue-avatar {
  flex-shrink: 0;
}

.clue-info { flex: 1; min-width: 0; }

.clue-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #5D4E3A;
}

.clue-meta {
  font-size: 12px;
  color: #8B7355;
  margin-bottom: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-item {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.clue-time {
  font-size: 11px;
  color: #B5A48C;
}

.clue-action {
  flex-shrink: 0;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.detail-panel {
  padding: 24px;
  min-height: 600px;
}

.empty-detail {
  text-align: center;
  padding: 80px 20px;
}

.empty-title {
  font-size: 18px;
  color: #8B4513;
  font-weight: 600;
  margin-bottom: 8px;
}

.empty-desc {
  color: #B5A48C;
  font-size: 14px;
}

.detail-header {
  display: flex;
  gap: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #E8D8C4;
  margin-bottom: 20px;
}

.avatar-section {
  text-align: center;
}

.info-section { flex: 1; }

.detail-name {
  font-size: 26px;
  font-weight: 700;
  color: #8B4513;
  margin-bottom: 12px;
}

.detail-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}

.detail-meta {
  margin-bottom: 16px;
}

.meta-row {
  font-size: 14px;
  color: #5D4E3A;
  margin-bottom: 4px;
}

.meta-label {
  color: #8B7355;
  margin-right: 4px;
}

.detail-actions {
  display: flex;
  gap: 10px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #8B4513;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #F4A460;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 14px;
}

.photo-item {
  background: #FFFAF0;
  border: 1px solid #E8D8C4;
  border-radius: 10px;
  overflow: hidden;
}

.photo-thumb {
  height: 120px;
  background: linear-gradient(135deg, #F5F0E6, #E8D8C4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  overflow: hidden;
}

.photo-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-thumb .photo-emoji {
  font-size: 60px;
  opacity: 0.6;
}

.photo-info {
  padding: 10px 12px;
}

.photo-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  color: #5D4E3A;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.photo-meta {
  font-size: 12px;
  color: #8B7355;
  margin-bottom: 6px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.meta-tag {
  background: #FFF5E6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.photo-footer {
  font-size: 12px;
  color: #B5A48C;
}

.claim-dialog {
  padding: 8px 0;
}

.claim-info {
  margin-bottom: 16px;
  text-align: center;
}

.claim-form {
  padding: 8px 0;
}

.selected-person-info {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: #FFFAF0;
  border-radius: 8px;
  border: 1px solid #E8D8C4;
}

.person-details {
  flex: 1;
}

.person-name {
  font-weight: 600;
  font-size: 16px;
  color: #8B4513;
  margin-bottom: 4px;
}

.person-desc {
  font-size: 13px;
  color: #8B7355;
}

.form-hint {
  font-size: 12px;
  color: #8B7355;
  margin-left: 8px;
}
</style>
