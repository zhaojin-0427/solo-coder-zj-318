<template>
  <div class="migration-map-page">
    <div class="page-header">
      <div class="page-title">
        <el-icon><LocationFilled /></el-icon>
        家族迁徙地图
      </div>
      <div class="page-subtitle">串联人物迁居、照片拍摄、回忆发生，可视化家族跨越时空的生命脉络</div>
    </div>

    <div class="filter-bar card-warm">
      <div class="filter-group">
        <label class="filter-label">年代筛选</label>
        <el-select v-model="filterDecade" placeholder="全部年代" clearable style="width: 140px">
          <el-option v-for="d in decadeOptions" :key="d.value" :label="d.label" :value="d.value" />
        </el-select>
      </div>

      <div class="filter-group">
        <label class="filter-label">人物筛选</label>
        <el-select v-model="filterPersonId" placeholder="全部人物" clearable filterable style="width: 180px">
          <el-option v-for="p in personOptions" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>

      <div class="filter-group">
        <label class="filter-label">地点搜索</label>
        <el-input v-model="filterLocation" placeholder="搜索地点..." clearable style="width: 200px">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>

      <div class="filter-group">
        <label class="filter-label">事件类型</label>
        <el-select v-model="filterNodeType" placeholder="全部类型" clearable style="width: 150px">
          <el-option v-for="t in nodeTypeOptions" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>

      <div class="filter-group">
        <label class="filter-label">包含冲突</label>
        <el-switch v-model="includeConflicted" />
      </div>

      <div style="flex: 1"></div>

      <el-button type="primary" class="btn-primary-warm" @click="loadData">
        <el-icon><Refresh /></el-icon>刷新数据
      </el-button>
      <el-button @click="syncTimeline">
        <el-icon><RefreshRight /></el-icon>同步时间线
      </el-button>
      <el-button type="success" plain @click="showTimeline = !showTimeline">
        <el-icon><List /></el-icon>{{ showTimeline ? '隐藏时间线' : '显示时间线' }}
      </el-button>
    </div>

    <div class="stats-summary card-warm" v-if="spacetimeStats">
      <div class="summary-item">
        <div class="summary-num">{{ spacetimeStats.total_nodes || 0 }}</div>
        <div class="summary-label">时空节点总数</div>
      </div>
      <div class="summary-item">
        <div class="summary-num" style="color:#10B981">{{ spacetimeStats.confirmed_nodes || 0 }}</div>
        <div class="summary-label">已确认节点</div>
      </div>
      <div class="summary-item">
        <div class="summary-num" style="color:#F59E0B">{{ spacetimeStats.pending_nodes || 0 }}</div>
        <div class="summary-label">待确认节点</div>
      </div>
      <div class="summary-item">
        <div class="summary-num" style="color:#DC2626">{{ spacetimeStats.conflicted_nodes || 0 }}</div>
        <div class="summary-label">存在冲突</div>
      </div>
      <div class="summary-item">
        <div class="summary-num" style="color:#8B5CF6">{{ spacetimeStats.photos_with_location || 0 }}</div>
        <div class="summary-label">已定位照片</div>
      </div>
      <div class="summary-item">
        <div class="summary-num" style="color:#0EA5E9">{{ spacetimeStats.persons_with_nodes || 0 }}</div>
        <div class="summary-label">有轨迹人物</div>
      </div>
      <div class="summary-item">
        <div class="summary-num" style="color:#EC4899">{{ spacetimeStats.migration_nodes || 0 }}</div>
        <div class="summary-label">迁居记录</div>
      </div>
      <div class="summary-item">
        <div class="summary-num" style="color:#F97316">{{ spacetimeStats.location_conflicts_pending || 0 }}</div>
        <div class="summary-label">地点冲突待确认</div>
      </div>
    </div>

    <div class="main-content">
      <div class="map-section card-warm">
        <div class="section-header">
          <h3><el-icon><MapLocation /></el-icon> 地点分布图</h3>
          <span class="sub-hint">（节点越大代表事件越多）</span>
        </div>
        <div ref="mapChart" class="map-canvas" v-loading="loading"></div>
      </div>

      <div class="timeline-section card-warm" v-if="showTimeline" :class="{ collapsed: !showTimeline }">
        <div class="section-header">
          <h3><el-icon><Clock /></el-icon> 家族时空时间线</h3>
          <div class="timeline-controls">
            <el-button size="small" :disabled="playing" @click="playTimeline">
              <el-icon><VideoPlay /></el-icon>{{ playing ? '播放中...' : '自动播放' }}
            </el-button>
            <el-button size="small" @click="stopTimeline" v-if="playing">
              <el-icon><VideoPause /></el-icon>停止
            </el-button>
            <el-slider
              v-if="timelineNodes.length > 0"
              v-model="currentPlayIndex"
              :min="0"
              :max="timelineNodes.length - 1"
              :step="1"
              :disabled="playing"
              style="width: 200px; margin-left: 12px;"
              @change="handleSliderChange"
            />
          </div>
        </div>

        <div class="timeline-list-wrap">
          <div v-if="!timelineNodes.length && !loading" class="empty-timeline">
            <el-icon :size="48" style="color:#D4A574; margin-bottom:12px;"><FolderOpened /></el-icon>
            <div>暂无时空节点数据</div>
            <div style="font-size:13px; margin-top:8px;">尝试调整筛选条件，或点击"同步时间线"从已有数据生成</div>
          </div>

          <el-timeline v-else>
            <el-timeline-item
              v-for="(node, idx) in timelineNodes"
              :key="node.id"
              :timestamp="formatNodeTime(node)"
              :type="getNodeTypeColor(node)"
              :hollow="node.status === 'conflicted'"
              :class="{ 'playing-active': playing && idx === currentPlayIndex }"
            >
              <div class="timeline-node-card" @click="openNodeDetail(node)">
                <div class="tn-header">
                  <el-tag :type="getNodeTagType(node)" size="small" effect="light">
                    {{ getNodeIcon(node) }} {{ node.node_type_display }}
                  </el-tag>
                  <el-tag v-if="node.status === 'conflicted'" size="small" type="danger" effect="dark" style="margin-left:6px;">
                    ⚠️ {{ node.conflict_field_display }}
                  </el-tag>
                  <el-tag v-else-if="node.status === 'confirmed'" size="small" type="success" effect="plain">已确认</el-tag>
                  <el-tag v-else size="small" type="warning" effect="plain">待确认</el-tag>
                  <span style="flex:1"></span>
                  <el-button size="small" text type="primary" @click.stop="openNodeDetail(node)">
                    查看详情 <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </div>
                <div class="tn-title">{{ node.title }}</div>
                <div class="tn-meta">
                  <span v-if="node.related_person_detail" class="tn-person">
                    👤 {{ node.related_person_detail.name }}
                  </span>
                  <span v-if="node.original_location || node.location_detail" class="tn-location">
                    📍 {{ node.original_location || node.location_detail?.standardized_name || '地点不详' }}
                  </span>
                  <span v-if="node.from_location_detail" class="tn-location">
                    ← 迁出: {{ node.from_location_detail.standardized_name }}
                  </span>
                </div>
                <div class="tn-desc" v-if="node.description">{{ node.description }}</div>
                <div class="tn-assets" v-if="node.related_photo_detail || node.related_memory_title">
                  <el-tag v-if="node.related_photo_detail" size="small" effect="plain" type="info">
                    📷 关联照片
                  </el-tag>
                  <el-tag v-if="node.related_memory_title" size="small" effect="plain" type="warning">
                    📜 关联回忆
                  </el-tag>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>

    <el-dialog v-model="showNodeDetail" :title="currentNode?.title || '节点详情'" width="760px" destroy-on-close>
      <div v-if="currentNode" class="node-detail-content">
        <div class="detail-row">
          <div class="detail-label">节点类型</div>
          <div class="detail-value">
            <el-tag :type="getNodeTagType(currentNode)" size="small">{{ getNodeIcon(currentNode) }} {{ currentNode.node_type_display }}</el-tag>
            <el-tag v-if="currentNode.status === 'conflicted'" size="small" type="danger" effect="dark" style="margin-left:6px;">
              ⚠️ {{ currentNode.conflict_field_display }}
            </el-tag>
            <el-tag v-else-if="currentNode.status === 'confirmed'" size="small" type="success" effect="plain">已确认</el-tag>
            <el-tag v-else size="small" type="warning" effect="plain">待确认</el-tag>
          </div>
        </div>

        <div class="detail-row">
          <div class="detail-label">时间</div>
          <div class="detail-value">{{ formatNodeTime(currentNode) }}</div>
        </div>

        <div class="detail-row">
          <div class="detail-label">地点</div>
          <div class="detail-value">
            <span v-if="currentNode.from_location_detail">
              <el-tag type="info" effect="plain">迁出: {{ currentNode.from_location_detail.standardized_name }}</el-tag>
              <span style="margin:0 8px;">→</span>
            </span>
            <span v-if="currentNode.location_detail">
              <el-tag type="warning" effect="plain">
                {{ currentNode.location_detail.standardized_name || currentNode.original_location }}
              </el-tag>
            </span>
            <span v-else-if="currentNode.original_location">
              {{ currentNode.original_location }}
            </span>
            <span v-else style="color:#999;">地点不详</span>
          </div>
        </div>

        <div class="detail-row">
          <div class="detail-label">关联人物</div>
          <div class="detail-value">
            <span v-if="currentNode.related_person_detail">{{ currentNode.related_person_detail.name }}</span>
            <span v-else style="color:#999;">无关联人物</span>
          </div>
        </div>

        <div class="detail-row" v-if="currentNode.description">
          <div class="detail-label">事件描述</div>
          <div class="detail-value description">{{ currentNode.description }}</div>
        </div>

        <div class="detail-row" v-if="currentNode.related_photo_detail">
          <div class="detail-label">关联照片</div>
          <div class="detail-value">
            <div class="linked-photo-card" @click="goToPhoto(currentNode.related_photo_id)">
              <div class="lpc-thumb">📷</div>
              <div>
                <div class="lpc-title">{{ currentNode.related_photo_detail.title }}</div>
                <div class="lpc-meta">{{ currentNode.related_photo_detail.era_display }} · {{ currentNode.related_photo_detail.scene_display }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-row" v-if="currentNode.related_memory_title">
          <div class="detail-label">关联回忆</div>
          <div class="detail-value">
            <el-tag size="large" type="warning" effect="light" @click="goToMemory(currentNode.related_memory_id)" style="cursor:pointer;">
              📜 {{ currentNode.related_memory_title }}
            </el-tag>
          </div>
        </div>

        <div class="detail-row" v-if="currentNode.related_conflict_detail">
          <div class="detail-label">关联冲突</div>
          <div class="detail-value">
            <el-alert
              :title="`${currentNode.related_conflict_detail.conflict_field_display} - ${currentNode.related_conflict_detail.description}`"
              type="warning"
              :closable="false"
              show-icon
            />
            <div style="margin-top:8px;">
              <div style="font-size:12px; color:#8B7355; margin-bottom:4px;">版本A（原版本）：{{ currentNode.related_conflict_detail.version_a_author }}</div>
              <div style="background:#FFFAF0; padding:8px; border-radius:6px; font-size:13px;">{{ currentNode.related_conflict_detail.version_a }}</div>
              <div style="font-size:12px; color:#8B7355; margin:8px 0 4px;">版本B（新版本）：{{ currentNode.related_conflict_detail.version_b_author }}</div>
              <div style="background:#FEF3C7; padding:8px; border-radius:6px; font-size:13px;">{{ currentNode.related_conflict_detail.version_b }}</div>
            </div>
            <el-button size="small" type="warning" plain style="margin-top:8px;" @click="goToConfirm(currentNode.related_conflict_id)">
              → 前往家庭确认台处理
            </el-button>
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="warning" plain @click="openCreateTaskFromNode(currentNode)">
            <el-icon><EditPen /></el-icon>发起采集任务
          </el-button>
          <el-button v-if="currentNode.related_person_id" type="primary" plain @click="goToPerson(currentNode.related_person_id)">
            <el-icon><User /></el-icon>查看人物档案
          </el-button>
          <el-button type="info" plain @click="showNodeDetail = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showCreateTask" title="从节点发起采集任务" width="520px" destroy-on-close>
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务类型" required>
          <el-select v-model="taskForm.task_type" style="width:100%">
            <el-option label="人物身份确认" value="identity_confirm" />
            <el-option label="旧称/别名补充" value="old_name_supplement" />
            <el-option label="迁居信息补充" value="migration_supplement" />
            <el-option label="事件背景口述" value="event_narration" />
            <el-option label="亲属关系校验" value="relation_verify" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" placeholder="自动生成，可修改" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" placeholder="自动生成，可修改" />
        </el-form-item>
        <el-form-item label="分派方式">
          <el-radio-group v-model="taskForm.assign_type">
            <el-radio value="family">全家开放</el-radio>
            <el-radio value="specific">指定人员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分派对象" v-if="taskForm.assign_type === 'specific'">
          <el-input v-model="taskForm.assigned_to" placeholder="指定家属姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateTask = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitCreateTask">创建任务</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  LocationFilled, Search, Refresh, RefreshRight, List, MapLocation, Clock,
  VideoPlay, VideoPause, ArrowRight, User, EditPen, FolderOpened
} from '@element-plus/icons-vue'
import { timeline as timelineApi, spacetime as spacetimeApi, persons as personsApi, tasks as tasksApi } from '@/api'
import * as echarts from 'echarts'

const router = useRouter()

const loading = ref(false)
const spacetimeStats = ref(null)
const timelineNodes = ref([])
const personOptions = ref([])
const locationAggregate = ref([])

const filterDecade = ref('')
const filterPersonId = ref(null)
const filterLocation = ref('')
const filterNodeType = ref('')
const includeConflicted = ref(false)
const showTimeline = ref(true)

const showNodeDetail = ref(false)
const currentNode = ref(null)

const showCreateTask = ref(false)
const taskForm = ref({
  task_type: 'migration_supplement',
  title: '',
  description: '',
  assign_type: 'family',
  assigned_to: ''
})

const playing = ref(false)
const currentPlayIndex = ref(0)
let playTimer = null

const mapChart = ref(null)
let mapChartInstance = null

const decadeOptions = [
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
]

const nodeTypeOptions = [
  { value: 'birth', label: '出生' },
  { value: 'death', label: '逝世' },
  { value: 'migration', label: '迁居' },
  { value: 'photo', label: '照片拍摄' },
  { value: 'memory', label: '回忆事件' },
  { value: 'event', label: '重要事件' },
  { value: 'task_result', label: '采集任务结果' },
]

const getNodeTypeColor = (node) => {
  const colorMap = {
    birth: 'success',
    death: 'info',
    migration: 'warning',
    photo: 'primary',
    memory: 'danger',
    event: '',
    task_result: ''
  }
  return colorMap[node.node_type] || ''
}

const getNodeTagType = (node) => {
  const typeMap = {
    birth: 'success',
    death: 'info',
    migration: 'warning',
    photo: 'primary',
    memory: 'danger',
    event: '',
    task_result: ''
  }
  return typeMap[node.node_type] || ''
}

const getNodeIcon = (node) => {
  const iconMap = {
    birth: '🎂',
    death: '🕯️',
    migration: '🏠',
    photo: '📷',
    memory: '📜',
    event: '📌',
    task_result: '✅'
  }
  return iconMap[node.node_type] || '📍'
}

const formatNodeTime = (node) => {
  if (node.year) {
    return `${node.year}年${node.month ? node.month + '月' : ''}${node.day ? node.day + '日' : ''}`
  }
  if (node.decade) {
    return `${node.decade.replace('s', '')}年代`
  }
  return '年份不详'
}

const loadPersons = async () => {
  try {
    const res = await personsApi.simple()
    personOptions.value = res || []
  } catch (e) {
    personOptions.value = []
  }
}

const loadSpacetimeStats = async () => {
  try {
    const res = await spacetimeApi.stats()
    spacetimeStats.value = res
  } catch (e) {
    spacetimeStats.value = {
      total_nodes: 0, confirmed_nodes: 0, pending_nodes: 0, conflicted_nodes: 0,
      photos_with_location: 0, persons_with_nodes: 0, migration_nodes: 0,
      location_conflicts_pending: 0
    }
  }
}

const loadTimelineNodes = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterDecade.value) params.decade = filterDecade.value
    if (filterPersonId.value) params.person_id = filterPersonId.value
    if (filterLocation.value) params.location_keyword = filterLocation.value
    if (filterNodeType.value) params.node_type = filterNodeType.value
    if (includeConflicted.value) params.include_conflicted = true
    params.page_size = 500

    const res = await timelineApi.query(params)
    timelineNodes.value = res?.results || []
    currentPlayIndex.value = 0
  } catch (e) {
    timelineNodes.value = []
    ElMessage.error('加载时间线失败')
  } finally {
    loading.value = false
    await nextTick()
    renderMapChart()
  }
}

const loadLocationAggregate = async () => {
  try {
    const params = { group_by: 'location' }
    if (filterPersonId.value) params.person_id = filterPersonId.value
    if (includeConflicted.value) params.include_conflicted = true
    const res = await timelineApi.aggregate(params)
    locationAggregate.value = res?.results || []
  } catch (e) {
    locationAggregate.value = []
  }
}

const loadData = async () => {
  await Promise.all([
    loadSpacetimeStats(),
    loadTimelineNodes(),
    loadLocationAggregate()
  ])
}

const syncTimeline = async () => {
  try {
    await ElMessageBox.confirm(
      '将从人物档案、迁居记录、照片、回忆、采集任务中同步生成时间线节点，是否继续？',
      '同步时间线',
      { type: 'warning', confirmButtonText: '确认同步', cancelButtonText: '取消' }
    )
    const res = await timelineApi.sync('all')
    ElMessage.success(`同步完成，新增 ${res?.created_count || 0} 个节点`)
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('同步失败')
  }
}

const renderMapChart = () => {
  if (!mapChart.value) return
  if (mapChartInstance) mapChartInstance.dispose()
  mapChartInstance = echarts.init(mapChart.value)

  const data = [...locationAggregate.value].slice(0, 30)
  if (!data.length) {
    const option = {
      title: {
        text: '暂无地点数据',
        left: 'center',
        top: 'center',
        textStyle: { color: '#B5A48C', fontSize: 16, fontWeight: 'normal' }
      },
      backgroundColor: 'transparent'
    }
    mapChartInstance.setOption(option)
    return
  }

  const maxVal = Math.max(...data.map(d => d.count), 1)
  const colors = ['#8B4513', '#D2691E', '#F4A460', '#C0392B', '#E74C3C', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899']

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => `${params.name}<br/>节点数: ${params.value[2]} 个`
    },
    grid: { left: 40, right: 40, top: 30, bottom: 40 },
    xAxis: {
      type: 'value',
      show: false,
      min: 0,
      max: 100
    },
    yAxis: {
      type: 'value',
      show: false,
      min: 0,
      max: 100
    },
    series: [{
      type: 'scatter',
      symbolSize: (val) => Math.max(12, (val[2] / maxVal) * 60),
      data: data.map((d, i) => ({
        name: d.name,
        value: [
          10 + (i % 5) * 18 + Math.random() * 8,
          15 + Math.floor(i / 5) * 22 + Math.random() * 10,
          d.count
        ],
        itemStyle: {
          color: colors[i % colors.length],
          opacity: 0.8,
          shadowBlur: 10,
          shadowColor: 'rgba(139, 69, 19, 0.3)'
        }
      })),
      label: {
        show: true,
        formatter: (p) => p.name.length > 6 ? p.name.slice(0, 6) + '..' : p.name,
        position: 'top',
        color: '#5D4E3A',
        fontSize: 11,
        fontWeight: 600
      },
      emphasis: {
        itemStyle: {
          opacity: 1,
          shadowBlur: 20
        },
        label: { fontSize: 13, fontWeight: 'bold' }
      }
    }]
  }
  mapChartInstance.setOption(option)
}

const openNodeDetail = (node) => {
  currentNode.value = node
  showNodeDetail.value = true
}

const goToPhoto = (id) => {
  router.push('/photos')
}

const goToMemory = (id) => {
  router.push('/memories')
}

const goToPerson = (id) => {
  router.push({ path: '/persons', query: { person_id: id } })
}

const goToConfirm = (id) => {
  router.push('/confirm')
}

const openCreateTaskFromNode = (node) => {
  currentNode.value = node
  taskForm.value = {
    task_type: node.node_type === 'migration' ? 'migration_supplement' : 'event_narration',
    title: `时空节点补注：${node.title}`,
    description: `节点：${node.title}\n时间：${formatNodeTime(node)}\n地点：${node.original_location || node.location_detail?.standardized_name || '不详'}`,
    assign_type: 'family',
    assigned_to: ''
  }
  showCreateTask.value = true
  showNodeDetail.value = false
}

const submitCreateTask = async () => {
  if (!currentNode.value) return
  try {
    const res = await timelineApi.createTask(currentNode.value.id, taskForm.value)
    ElMessage.success('采集任务创建成功')
    showCreateTask.value = false
    if (res?.task?.id) {
      router.push({ path: '/tasks', query: { task_id: res.task.id } })
    }
  } catch (e) {
    ElMessage.error('创建任务失败')
  }
}

const playTimeline = () => {
  if (!timelineNodes.value.length) return
  playing.value = true
  currentPlayIndex.value = 0
  playTimer = setInterval(() => {
    if (currentPlayIndex.value >= timelineNodes.value.length - 1) {
      stopTimeline()
      return
    }
    currentPlayIndex.value++
    const card = document.querySelector('.timeline-node-card.playing-active')
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 2000)
}

const stopTimeline = () => {
  playing.value = false
  if (playTimer) {
    clearInterval(playTimer)
    playTimer = null
  }
}

const handleSliderChange = (val) => {
  currentPlayIndex.value = val
}

const handleResize = () => {
  mapChartInstance?.resize()
}

watch([filterDecade, filterPersonId, filterLocation, filterNodeType, includeConflicted], () => {
  loadData()
})

onMounted(() => {
  loadPersons()
  loadData()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.migration-map-page {
  color: #5D4E3A;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 18px 22px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: #8B7355;
  white-space: nowrap;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 12px;
  padding: 18px 22px;
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
  padding: 10px 8px;
  background: #FFFAF0;
  border-radius: 10px;
  border: 1px solid #F5EDE0;
}

.summary-num {
  font-size: 26px;
  font-weight: 700;
  color: #8B4513;
  line-height: 1.2;
}

.summary-label {
  font-size: 12px;
  color: #8B7355;
  margin-top: 4px;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.map-section,
.timeline-section {
  padding: 20px 24px;
}

.section-header {
  display: flex;
  align-items: center;
  padding-bottom: 14px;
  margin-bottom: 14px;
  border-bottom: 1px solid #F5EDE0;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #8B4513;
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
}

.sub-hint {
  font-size: 12px;
  color: #B5A48C;
  margin-left: 8px;
}

.timeline-controls {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.map-canvas {
  width: 100%;
  height: 560px;
}

.timeline-list-wrap {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.timeline-list-wrap::-webkit-scrollbar {
  width: 6px;
}
.timeline-list-wrap::-webkit-scrollbar-thumb {
  background: #D4A574;
  border-radius: 3px;
}

.timeline-node-card {
  background: #FFFAF0;
  border: 1px solid #F5EDE0;
  border-radius: 10px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.timeline-node-card:hover {
  border-color: #D2691E;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.1);
  background: #FFF8F0;
}

.playing-active .timeline-node-card {
  border-color: #D2691E;
  background: #FFF3E0;
  box-shadow: 0 0 0 3px rgba(210, 105, 30, 0.2);
}

.tn-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.tn-title {
  font-size: 15px;
  font-weight: 600;
  color: #5D4E3A;
  margin-bottom: 6px;
}

.tn-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: #8B7355;
  margin-bottom: 6px;
}

.tn-desc {
  font-size: 13px;
  color: #6B5B45;
  background: #FFF8F0;
  padding: 6px 10px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.tn-assets {
  display: flex;
  gap: 6px;
}

.empty-timeline {
  text-align: center;
  padding: 40px 20px;
  color: #B5A48C;
}

.node-detail-content {
  color: #5D4E3A;
}

.detail-row {
  display: flex;
  margin-bottom: 16px;
}

.detail-label {
  width: 100px;
  font-size: 13px;
  color: #8B7355;
  font-weight: 600;
  flex-shrink: 0;
  padding-top: 2px;
}

.detail-value {
  flex: 1;
  font-size: 14px;
}

.detail-value.description {
  background: #FFFAF0;
  padding: 10px 14px;
  border-radius: 8px;
  line-height: 1.6;
}

.linked-photo-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #FFFAF0;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.linked-photo-card:hover {
  background: #FFF3E0;
}

.lpc-thumb {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #D2691E, #F4A460);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.lpc-title {
  font-weight: 600;
  color: #5D4E3A;
}

.lpc-meta {
  font-size: 12px;
  color: #8B7355;
  margin-top: 2px;
}

.detail-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid #F5EDE0;
  margin-top: 8px;
}
</style>
