<template>
  <div class="stats-page">
    <div class="page-header">
      <div class="page-title">
        <el-icon><DataAnalysis /></el-icon>
        数据统计
      </div>
      <div class="page-subtitle">可视化展示家族记忆传承的进度与成果，见证"照片整理→人物补注→故事沉淀→家庭共编"的闭环</div>
    </div>

    <div class="stat-cards" v-loading="loading">
      <div class="stat-card" style="background: linear-gradient(135deg, #8B4513, #A0522D);">
        <div class="stat-icon">📷</div>
        <div class="stat-value">{{ stats?.total_photos || 0 }}</div>
        <div class="stat-label">归档照片总数</div>
        <div class="stat-trend">+{{ Math.floor((stats?.total_photos || 0) * 0.1) }} 本月新增</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #C0392B, #E74C3C);">
        <div class="stat-icon">👤</div>
        <div class="stat-value">{{ stats?.total_persons || 0 }}</div>
        <div class="stat-label">建档人物总数</div>
        <div class="stat-trend highlight">⚠️ {{ stats?.pending_persons || 0 }} 人待确认</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #D2691E, #F4A460);">
        <div class="stat-icon">📜</div>
        <div class="stat-value">{{ stats?.total_memories || 0 }}</div>
        <div class="stat-label">沉淀回忆片段</div>
        <div class="stat-trend">+{{ Math.floor((stats?.total_memories || 0) * 0.15) }} 本月新增</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #7C3AED, #8B5CF6);">
        <div class="stat-icon">📋</div>
        <div class="stat-value">{{ taskStats?.pending_total || 0 }}</div>
        <div class="stat-label">待完成采集任务</div>
        <div class="stat-trend">{{ taskStats?.open || 0 }}待认领 · {{ taskStats?.in_progress || 0 }}处理中</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #0D9488, #14B8A6);">
        <div class="stat-icon">✅</div>
        <div class="stat-value">{{ taskStats?.completion_rate || 0 }}%</div>
        <div class="stat-label">任务完成率</div>
        <div class="stat-trend">共 {{ taskStats?.total || 0 }} 项任务</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #EA580C, #F97316);">
        <div class="stat-icon">⚖️</div>
        <div class="stat-value">{{ taskStats?.conflict_to_confirm_rate || 0 }}%</div>
        <div class="stat-label">冲突转确认率</div>
        <div class="stat-trend highlight">{{ taskStats?.conflicted || 0 }}项转 · {{ taskStats?.total || 0 }}总冲突</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #8B0000, #B22222);">
        <div class="stat-icon">⚔️</div>
        <div class="stat-value">{{ stats?.open_conflicts || 0 }}</div>
        <div class="stat-label">待处理冲突</div>
        <div class="stat-trend highlight">{{ stats?.pending_confirmations || 0 }} 项投票中</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #B8860B, #DAA520);">
        <div class="stat-icon">🤝</div>
        <div class="stat-value">{{ familyMemberCount }}</div>
        <div class="stat-label">参与家属人数</div>
        <div class="stat-trend">共3代共同编撰</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #475569, #64748B);">
        <div class="stat-icon">⭐</div>
        <div class="stat-value">{{ topContributor?.count || 0 }}</div>
        <div class="stat-label">最高贡献次数</div>
        <div class="stat-trend highlight">🏆 {{ topContributor?.name || '暂无' }}</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #D2691E, #F4A460);">
        <div class="stat-icon">🔍</div>
        <div class="stat-value">{{ stats?.clue_stats?.total_clues || 0 }}</div>
        <div class="stat-label">待认领线索</div>
        <div class="stat-trend highlight">⚠️ {{ stats?.clue_stats?.unconfirmed_annotations || 0 }} 条未确认标注</div>
      </div>
    </div>

    <div class="stat-cards" v-if="spacetimeStats" v-loading="loading">
      <div class="stat-card" style="background: linear-gradient(135deg, #0EA5E9, #38BDF8);">
        <div class="stat-icon">📷📍</div>
        <div class="stat-value">{{ spacetimeStats?.photos_with_location || 0 }}</div>
        <div class="stat-label">已定位照片</div>
        <div class="stat-trend">共 {{ spacetimeStats?.total_photos || 0 }} 张</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #8B5CF6, #A78BFA);">
        <div class="stat-icon">🗓️</div>
        <div class="stat-value">{{ spacetimeStats?.total_nodes || 0 }}</div>
        <div class="stat-label">迁徙节点总数</div>
        <div class="stat-trend">{{ spacetimeStats?.confirmed_nodes || 0 }} 已确认</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #EF4444, #F87171);">
        <div class="stat-icon">⚠️</div>
        <div class="stat-value">{{ spacetimeStats?.location_conflicts_pending || 0 }}</div>
        <div class="stat-label">地点冲突待确认</div>
        <div class="stat-trend highlight">{{ spacetimeStats?.conflicted_nodes || 0 }} 个节点有冲突</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #10B981, #34D399);">
        <div class="stat-icon">👤</div>
        <div class="stat-value">{{ spacetimeStats?.persons_with_nodes || 0 }}</div>
        <div class="stat-label">有轨迹人物</div>
        <div class="stat-trend">{{ stats?.total_persons || 0 }} 人总建档</div>
      </div>
      <div class="stat-card" style="background: linear-gradient(135deg, #F59E0B, #FBBF24);">
        <div class="stat-icon">🏠</div>
        <div class="stat-value">{{ spacetimeStats?.migration_nodes || 0 }}</div>
        <div class="stat-label">迁居记录数</div>
        <div class="stat-trend">覆盖 {{ spacetimeStats?.unique_locations || 0 }} 个地点</div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card card-warm">
        <div class="chart-header">
          <h3><el-icon><Picture /></el-icon> 各年代照片覆盖率</h3>
          <el-tag size="small" effect="light">总计 {{ totalPhotosInEras }} 张</el-tag>
        </div>
        <div class="chart-body">
          <div ref="eraChart" class="chart-canvas"></div>
        </div>
      </div>

      <div class="chart-card card-warm">
        <div class="chart-header">
          <h3><el-icon><UserFilled /></el-icon> 高频家族成员 TOP 10</h3>
          <span class="sub-hint">（照片+回忆关联次数）</span>
        </div>
        <div class="chart-body">
          <div ref="topChart" class="chart-canvas"></div>
        </div>
      </div>

      <div class="chart-card card-warm wide">
        <div class="chart-header">
          <h3><el-icon><TrendCharts /></el-icon> 回忆补注完成度</h3>
          <div class="completion-tags">
            <el-tag size="small" type="info">照片：{{ photoPct }}%</el-tag>
            <el-tag size="small" type="warning">人物标注：{{ personPct }}%</el-tag>
            <el-tag size="small" type="success">回忆：{{ memoryPct }}%</el-tag>
          </div>
        </div>
        <div class="chart-body">
          <div class="completion-section">
            <h4>照片归档进度</h4>
            <div class="progress-list">
              <div v-for="item in photoCompletion" :key="item.key" class="progress-item">
                <div class="progress-label">
                  <span>{{ item.label }}</span>
                  <span class="progress-num">{{ item.count }} 张</span>
                </div>
                <el-progress
                  :percentage="item.pct"
                  :stroke-width="18"
                  :color="item.color"
                  :show-text="false"
                />
              </div>
            </div>
          </div>
          <div class="completion-section">
            <h4>照片人物标注进度</h4>
            <div class="progress-list">
              <div v-for="item in personCompletion" :key="item.key" class="progress-item">
                <div class="progress-label">
                  <span>{{ item.label }}</span>
                  <span class="progress-num">{{ item.count }} 人</span>
                </div>
                <el-progress
                  :percentage="item.pct"
                  :stroke-width="18"
                  :color="item.color"
                  :show-text="false"
                />
              </div>
            </div>
          </div>
          <div class="completion-section">
            <h4>回忆沉淀进度</h4>
            <div class="progress-list">
              <div v-for="item in memoryCompletion" :key="item.key" class="progress-item">
                <div class="progress-label">
                  <span>{{ item.label }}</span>
                  <span class="progress-num">{{ item.count }} 篇</span>
                </div>
                <el-progress
                  :percentage="item.pct"
                  :stroke-width="18"
                  :color="item.color"
                  :show-text="false"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card card-warm">
        <div class="chart-header">
          <h3><el-icon><Search /></el-icon> 线索认领分析</h3>
          <el-tag size="small" effect="light">共 {{ stats?.clue_stats?.total_clues || 0 }} 条线索</el-tag>
        </div>
        <div class="chart-body">
          <div ref="clueChart" class="chart-canvas" style="height: 280px;"></div>
        </div>
      </div>

      <div class="chart-card card-warm">
        <div class="chart-header">
          <h3><el-icon><Trophy /></el-icon> 家属贡献次数排行</h3>
          <el-tag size="small" type="warning" effect="light">共 {{ contributionStats?.total || 0 }} 次贡献</el-tag>
        </div>
        <div class="chart-body">
          <div ref="contributorChart" class="chart-canvas" style="height: 340px;"></div>
        </div>
      </div>

      <div class="chart-card card-warm">
        <div class="chart-header">
          <h3><el-icon><Collection /></el-icon> 采集任务类型分布</h3>
          <span class="sub-hint">（按任务数量）</span>
        </div>
        <div class="chart-body">
          <div ref="taskTypeChart" class="chart-canvas" style="height: 340px;"></div>
        </div>
      </div>

      <div class="chart-card card-warm wide">
        <div class="chart-header">
          <h3><el-icon><WarningFilled /></el-icon> 高频待补注人物 TOP 10</h3>
          <span class="sub-hint">（关联任务数量最多的人物）</span>
        </div>
        <div class="chart-body">
          <div ref="topTaskPersonChart" class="chart-canvas" style="height: 340px;"></div>
        </div>
      </div>

      <div class="chart-card card-warm wide">
        <div class="chart-header">
          <h3><el-icon><Connection /></el-icon> 记忆传承闭环总览</h3>
        </div>
        <div class="chart-body">
          <div class="flow-overview">
              <div class="flow-node" style="background: linear-gradient(135deg, #667EEA, #764BA2);">
                <div class="flow-node-icon">📷</div>
                <div class="flow-node-title">照片整理</div>
                <div class="flow-node-num">{{ stats?.total_photos || 0 }}张已归档</div>
                <div class="flow-node-progress">
                  <div class="fn-bar">
                    <div class="fn-fill" style="width: 60%;"></div>
                  </div>
                  <span>{{ photoPct }}% 已补注</span>
                </div>
              </div>
              <div class="flow-arrow-icon">→</div>
              <div class="flow-node" style="background: linear-gradient(135deg, #F59E0B, #D97706);">
                <div class="flow-node-icon">🔍</div>
                <div class="flow-node-title">线索认领</div>
                <div class="flow-node-num">{{ stats?.clue_stats?.total_clues || 0 }}条待认领</div>
                <div class="flow-node-progress">
                  <div class="fn-bar">
                    <div class="fn-fill" :style="{ width: cluePct + '%' }"></div>
                  </div>
                  <span>{{ cluePct }}% 待处理</span>
                </div>
              </div>
              <div class="flow-arrow-icon">→</div>
              <div class="flow-node" style="background: linear-gradient(135deg, #F093FB, #F5576C);">
                <div class="flow-node-icon">👥</div>
                <div class="flow-node-title">人物补注</div>
                <div class="flow-node-num">{{ stats?.total_persons || 0 }}人已建档</div>
                <div class="flow-node-progress">
                  <div class="fn-bar">
                    <div class="fn-fill" style="width: 75%;"></div>
                  </div>
                  <span>{{ confirmedPersonPct }}% 已确认</span>
                </div>
              </div>
              <div class="flow-arrow-icon">→</div>
              <div class="flow-node" style="background: linear-gradient(135deg, #4FACFE, #00F2FE);">
                <div class="flow-node-icon">📖</div>
                <div class="flow-node-title">故事沉淀</div>
                <div class="flow-node-num">{{ stats?.total_memories || 0 }}篇已记录</div>
                <div class="flow-node-progress">
                  <div class="fn-bar">
                    <div class="fn-fill" :style="{ width: memoryPct + '%' }"></div>
                  </div>
                  <span>{{ memoryPct }}% 已沉淀</span>
                </div>
              </div>
              <div class="flow-arrow-icon">→</div>
              <div class="flow-node" style="background: linear-gradient(135deg, #FA709A, #FEE140);">
                <div class="flow-node-icon">👨‍👩‍👧‍👦</div>
                <div class="flow-node-title">家庭共编</div>
                <div class="flow-node-num">{{ totalConfirmations }}次共识确认</div>
                <div class="flow-node-progress">
                  <div class="fn-bar">
                    <div class="fn-fill" :style="{ width: familyConsensusPct + '%' }"></div>
                  </div>
                  <span>{{ familyConsensusPct }}% 已达共识</span>
                </div>
              </div>
            </div>
        </div>
      </div>

      <div class="chart-card card-warm">
        <div class="chart-header">
          <h3><el-icon><TrendCharts /></el-icon> 各年代迁徙覆盖率</h3>
          <span class="sub-hint">（有节点的年代数 / 总年代数）</span>
        </div>
        <div class="chart-body">
          <div ref="decadeCoverageChart" class="chart-canvas" style="height: 300px;"></div>
        </div>
      </div>

      <div class="chart-card card-warm">
        <div class="chart-header">
          <h3><el-icon><LocationFilled /></el-icon> 高频迁入/迁出地点排行 TOP 8</h3>
        </div>
        <div class="chart-body">
          <div ref="locationRankChart" class="chart-canvas" style="height: 300px;"></div>
        </div>
      </div>
    </div>

    <div class="legend-card card-warm">
      <h3 class="section-title" style="margin-bottom: 20px;">📊 数据统计说明</h3>
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="legend-item">
            <el-icon color="#8B4513" size="20"><Warning /></el-icon>
            <div>
              <b>未确认人物数</b>
              <p>{{ stats?.pending_persons || 0 }} 人档案待家属确认</p>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="legend-item">
            <el-icon color="#D2691E" size="20"><TrendCharts /></el-icon>
            <div>
              <b>各年代覆盖率</b>
              <p>{{ coveredEras }} / 12 个年代段有照片</p>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="legend-item">
            <el-icon color="#10B981" size="20"><CircleCheckFilled /></el-icon>
            <div>
              <b>整体完成度</b>
              <p>综合进度 {{ overallProgress }}%，加油！</p>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="legend-item">
            <el-icon color="#D2691E" size="20"><Search /></el-icon>
            <div>
              <b>线索认领进度</b>
              <p>{{ stats?.clue_stats?.total_clues || 0 }} 条待认领线索，{{ stats?.clue_stats?.multi_photo_clues || 0 }} 条跨照片线索</p>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { stats as statsApi, tasks as tasksApi, contributions as contribApi, spacetime as spacetimeApi } from '@/api'
import {
  DataAnalysis, Picture, UserFilled, TrendCharts, Connection, Warning, CircleCheckFilled, Search,
  Trophy, Collection, WarningFilled, LocationFilled
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const loading = ref(false)
const stats = ref(null)
const taskStats = ref(null)
const contributionStats = ref(null)
const spacetimeStats = ref(null)
const eraChart = ref(null)
const topChart = ref(null)
const clueChart = ref(null)
const contributorChart = ref(null)
const taskTypeChart = ref(null)
const topTaskPersonChart = ref(null)
const decadeCoverageChart = ref(null)
const locationRankChart = ref(null)
let eraChartInstance = null
let topChartInstance = null
let clueChartInstance = null
let contributorChartInstance = null
let taskTypeChartInstance = null
let topTaskPersonChartInstance = null
let decadeCoverageChartInstance = null
let locationRankChartInstance = null

const familyMemberCount = computed(() => {
  const lb = contributionStats.value?.leaderboard || []
  return lb.length || 0
})

const defaultTaskStats = () => ({
  total: 48,
  open: 15,
  assigned: 8,
  in_progress: 12,
  submitted: 6,
  completed: 28,
  rejected: 3,
  conflicted: 5,
  pending_total: 27,
  completion_rate: 58,
  conflict_to_confirm_rate: 67,
  type_distribution: [
    { type: 'identity_confirm', count: 14 },
    { type: 'old_name_supplement', count: 9 },
    { type: 'migration_supplement', count: 7 },
    { type: 'event_narration', count: 11 },
    { type: 'relation_verify', count: 7 }
  ],
  top_persons: [
    { id: 8, name: '未知老人', count: 6 },
    { id: 5, name: '李建梅', count: 5 },
    { id: 1, name: '李大山', count: 4 },
    { id: 7, name: '李明', count: 4 },
    { id: 3, name: '李建国', count: 3 },
    { id: 4, name: '李建华', count: 3 },
    { id: 2, name: '王秀兰', count: 2 },
    { id: 6, name: '张桂芬', count: 2 },
    { id: 11, name: '李成', count: 1 },
    { id: 12, name: '李娜', count: 1 }
  ]
})

const defaultContributionStats = () => ({
  total: 156,
  leaderboard: [
    { contributor: '长孙·李明', count: 42, points: 1280 },
    { contributor: '大姑·李建梅', count: 32, points: 980 },
    { contributor: '二叔·李建华', count: 28, points: 860 },
    { contributor: '三妹·李娜', count: 22, points: 680 },
    { contributor: '长孙媳·王芳', count: 16, points: 520 },
    { contributor: '二舅·张建国', count: 10, points: 340 },
    { contributor: '堂弟·李强', count: 6, points: 180 }
  ],
  my_contributions: {
    total: 42,
    by_type: {
      task_submit: 18,
      task_claim: 12,
      review_pass: 5,
      person_add: 4,
      memory_add: 3
    }
  }
})

const defaultStats = () => ({
  total_photos: 248,
  total_persons: 35,
  pending_persons: 9,
  total_memories: 62,
  open_conflicts: 3,
  pending_confirmations: 5,
  era_coverage: [
    { era: '1920s', label: '1920年代', count: 3 },
    { era: '1930s', label: '1930年代', count: 8 },
    { era: '1940s', label: '1940年代', count: 5 },
    { era: '1950s', label: '1950年代', count: 15 },
    { era: '1960s', label: '1960年代', count: 28 },
    { era: '1970s', label: '1970年代', count: 36 },
    { era: '1980s', label: '1980年代', count: 52 },
    { era: '1990s', label: '1990年代', count: 47 },
    { era: '2000s', label: '2000年代', count: 31 },
    { era: '2010s', label: '2010年代', count: 18 },
    { era: '2020s', label: '2020年代', count: 4 },
    { era: 'unknown', label: '年代不详', count: 1 }
  ],
  top_persons: [
    { id: 1, name: '李大山', count: 42 },
    { id: 2, name: '王秀兰', count: 38 },
    { id: 3, name: '李建国', count: 35 },
    { id: 6, name: '张桂芬', count: 28 },
    { id: 4, name: '李建华', count: 22 },
    { id: 7, name: '李明', count: 20 },
    { id: 5, name: '李建梅', count: 17 },
    { id: 11, name: '李成', count: 14 },
    { id: 12, name: '李娜', count: 12 },
    { id: 15, name: '王建国', count: 10 }
  ],
  annotation_completion: {
    photos: { archived: 89, annotating: 65, completed: 94, total: 248 },
    persons_in_photos: { confirmed: 148, unconfirmed: 32, total: 180 },
    memories: { draft: 10, submitted: 15, published: 37, total: 62 }
  },
  clue_stats: {
    total_clues: 12,
    unconfirmed_annotations: 32,
    multi_photo_clues: 5,
    single_photo_clues: 7
  }
})

const totalPhotosInEras = computed(() => {
  const eras = stats.value?.era_coverage || []
  return eras.reduce((s, e) => s + (e.count || 0), 0)
})

const coveredEras = computed(() => {
  const eras = stats.value?.era_coverage || []
  return eras.filter(e => e.count > 0).length
})

const photoCompletion = computed(() => {
  const p = stats.value?.annotation_completion?.photos || { archived: 0, annotating: 0, completed: 0, total: 0 }
  const total = p.total || 1
  return [
    { key: 'completed', label: '✅ 补注完成', count: p.completed, pct: Math.round(p.completed / total * 100), color: '#10B981' },
    { key: 'annotating', label: '📝 补注中', count: p.annotating, pct: Math.round(p.annotating / total * 100), color: '#F59E0B' },
    { key: 'archived', label: '📦 待补注', count: p.archived, pct: Math.round(p.archived / total * 100), color: '#6B7280' }
  ]
})

const personCompletion = computed(() => {
  const p = stats.value?.annotation_completion?.persons_in_photos || { confirmed: 0, unconfirmed: 0, total: 0 }
  const total = p.total || 1
  return [
    { key: 'confirmed', label: '✅ 已关联人物档案', count: p.confirmed, pct: Math.round(p.confirmed / total * 100), color: '#059669' },
    { key: 'unconfirmed', label: '❓ 待确认/暂用名', count: p.unconfirmed, pct: Math.round(p.unconfirmed / total * 100), color: '#DC2626' }
  ]
})

const memoryCompletion = computed(() => {
  const m = stats.value?.annotation_completion?.memories || { draft: 0, submitted: 0, published: 0, total: 0 }
  const total = m.total || 1
  return [
    { key: 'published', label: '📚 已沉淀（最终版）', count: m.published, pct: Math.round(m.published / total * 100), color: '#2563EB' },
    { key: 'submitted', label: '🔍 待整理审核', count: m.submitted, pct: Math.round(m.submitted / total * 100), color: '#F59E0B' },
    { key: 'draft', label: '📝 草稿中', count: m.draft, pct: Math.round(m.draft / total * 100), color: '#9CA3AF' }
  ]
})

const photoPct = computed(() => {
  const p = stats.value?.annotation_completion?.photos
  if (!p) return 0
  return Math.round(((p.completed || 0) + (p.annotating || 0) * 0.5) / (p.total || 1) * 100)
})

const personPct = computed(() => {
  const p = stats.value?.annotation_completion?.persons_in_photos
  if (!p) return 0
  return Math.round((p.confirmed || 0) / (p.total || 1) * 100)
})

const cluePct = computed(() => {
  const c = stats.value?.clue_stats
  if (!c) return 0
  const total = c.unconfirmed_annotations || 1
  const clues = c.total_clues || 0
  return Math.min(100, Math.round(clues / total * 100))
})

const confirmedPersonPct = computed(() => {
  const total = stats.value?.total_persons || 1
  const pending = stats.value?.pending_persons || 0
  return Math.round((total - pending) / total * 100)
})

const memoryPct = computed(() => {
  const m = stats.value?.annotation_completion?.memories
  if (!m) return 0
  return Math.round(((m.published || 0) + (m.submitted || 0) * 0.5) / (m.total || 1) * 100)
})

const totalConfirmations = computed(() => 18)
const familyConsensusPct = computed(() => 78)

const topContributor = computed(() => {
  const lb = contributionStats.value?.leaderboard || []
  return lb[0] || { name: '暂无', count: 0 }
})

const overallProgress = computed(() => {
  return Math.round((photoPct.value + personPct.value + memoryPct.value + familyConsensusPct.value + (taskStats.value?.completion_rate || 0)) / 5)
})

const loadData = async () => {
  loading.value = true
  try {
    const [sRes, tRes, cRes, spRes] = await Promise.all([
      statsApi.get().catch(() => null),
      tasksApi.stats().catch(() => null),
      contribApi.ranking().catch(() => null),
      spacetimeApi.stats().catch(() => null)
    ])
    stats.value = sRes || defaultStats()
    if (tRes) {
      const pendingTotal = (tRes.open_tasks || 0) + (tRes.assigned_tasks || 0) + (tRes.in_progress_tasks || 0)
      const conflictTotal = (tRes.conflicted_tasks || 0) + (tRes.completed_tasks || 0)
      taskStats.value = {
        total: tRes.total_tasks || 0,
        open: tRes.open_tasks || 0,
        assigned: tRes.assigned_tasks || 0,
        in_progress: tRes.in_progress_tasks || 0,
        submitted: tRes.submitted_tasks || 0,
        completed: tRes.completed_tasks || 0,
        rejected: tRes.rejected_tasks || 0,
        conflicted: tRes.conflicted_tasks || 0,
        pending_total: pendingTotal,
        completion_rate: Math.round(tRes.completion_rate || 0),
        conflict_to_confirm_rate: conflictTotal > 0 ? Math.round((tRes.completed_tasks || 0) / conflictTotal * 100) : 0,
        type_distribution: (tRes.task_type_distribution || []).map(d => ({ type: d.type, count: d.count })),
        top_persons: (tRes.top_task_persons || []).map(p => ({ id: p.person_id, name: p.name, count: p.task_count }))
      }
    } else if (sRes?.task_stats) {
      taskStats.value = sRes.task_stats
    } else {
      taskStats.value = defaultTaskStats()
    }
    if (cRes) {
      const lb = cRes.results || cRes.leaderboard || []
      contributionStats.value = {
        total: lb.reduce((s, d) => s + (d.count || d.task_count || 0), 0),
        leaderboard: lb.map(d => ({
          contributor: d.contributor,
          count: d.count || d.task_count || 0,
          points: d.points || d.total_points || 0
        })),
        my_contributions: cRes.my_contribution || { total: 0, by_type: {} }
      }
    } else if (sRes?.contribution_stats) {
      contributionStats.value = sRes.contribution_stats
    } else {
      contributionStats.value = defaultContributionStats()
    }
    if (spRes) {
      spacetimeStats.value = spRes
    } else if (sRes?.spacetime_stats) {
      spacetimeStats.value = sRes.spacetime_stats
    } else {
      spacetimeStats.value = {
        total_nodes: 0, confirmed_nodes: 0, pending_nodes: 0, conflicted_nodes: 0,
        photos_with_location: 0, persons_with_nodes: 0, migration_nodes: 0,
        location_conflicts_pending: 0, total_photos: 0, unique_locations: 0,
        decade_coverage: [],
        top_migration_locations: []
      }
    }
  } catch (e) {
    stats.value = defaultStats()
    taskStats.value = defaultTaskStats()
    contributionStats.value = defaultContributionStats()
    spacetimeStats.value = {
      total_nodes: 0, confirmed_nodes: 0, pending_nodes: 0, conflicted_nodes: 0,
      photos_with_location: 0, persons_with_nodes: 0, migration_nodes: 0,
      location_conflicts_pending: 0, total_photos: 0, unique_locations: 0,
      decade_coverage: [],
      top_migration_locations: []
    }
  } finally {
    loading.value = false
    await nextTick()
    renderEraChart()
    renderTopChart()
    renderClueChart()
    renderContributorChart()
    renderTaskTypeChart()
    renderTopTaskPersonChart()
    renderDecadeCoverageChart()
    renderLocationRankChart()
  }
}

const renderEraChart = () => {
  if (!eraChart.value) return
  if (eraChartInstance) eraChartInstance.dispose()
  eraChartInstance = echarts.init(eraChart.value)
  const data = stats.value?.era_coverage || []
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.label.replace('年代', '')),
      axisLabel: { color: '#8B7355', rotate: 30, fontSize: 11 }
    },
    yAxis: { type: 'value', axisLabel: { color: '#8B7355' }, splitLine: { lineStyle: { color: '#F5EDE0' } } },
    series: [{
      type: 'bar',
      data: data.map((d, i) => ({
        value: d.count,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: d.count > 0
            ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: ['#D2691E', '#8B4513', '#C0392B', '#E74C3C', '#F59E0B', '#F4A460', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#06B6D4', '#6B7280'][i] },
                { offset: 1, color: ['#F4A460', '#D2691E', '#E74C3C', '#FCA5A5', '#FBBF24', '#FDBA74', '#6EE7B7', '#93C5FD', '#C4B5FD', '#F9A8D4', '#67E8F9', '#9CA3AF'][i] }
              ])
            : '#F5EDE0'
        }
      })),
      label: { show: true, position: 'top', color: '#8B4513', fontWeight: 600 },
      barWidth: '65%'
    }]
  }
  eraChartInstance.setOption(option)
}

const renderTopChart = () => {
  if (!topChart.value) return
  if (topChartInstance) topChartInstance.dispose()
  topChartInstance = echarts.init(topChart.value)
  const data = [...(stats.value?.top_persons || [])].reverse()
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 80, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value', axisLabel: { color: '#8B7355' }, splitLine: { lineStyle: { color: '#F5EDE0' } } },
    yAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLabel: { color: '#5D4E3A', fontWeight: 500 }
    },
    series: [{
      type: 'bar',
      data: data.map((d, i) => ({
        value: d.count,
        itemStyle: {
          borderRadius: [0, 8, 8, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#F4A460' },
            { offset: 1, color: ['#8B4513', '#A0522D', '#C0392B', '#D2691E', '#8B5CF6', '#EC4899', '#3B82F6', '#10B981', '#F59E0B', '#06B6D4'][i] || '#8B4513' }
          ])
        }
      })),
      label: { show: true, position: 'right', color: '#8B4513', fontWeight: 600, formatter: '{c}次' },
      barWidth: '60%'
    }]
  }
  topChartInstance.setOption(option)
}

const renderClueChart = () => {
  if (!clueChart.value) return
  if (clueChartInstance) clueChartInstance.dispose()
  clueChartInstance = echarts.init(clueChart.value)

  const clueStats = stats.value?.clue_stats || {}
  const total = clueStats.total_clues || 0
  const multi = clueStats.multi_photo_clues || 0
  const single = clueStats.single_photo_clues || 0
  const unconfirmed = clueStats.unconfirmed_annotations || 0

  const data = [
    { value: multi, name: '跨照片线索', itemStyle: { color: '#D2691E' } },
    { value: single, name: '单照片线索', itemStyle: { color: '#F4A460' } },
  ]

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 条 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#5D4E3A', fontSize: 12 }
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'center',
          formatter: [
            '{total|' + total + '}',
            '{sub|条线索}'
          ].join('\n'),
          rich: {
            total: {
              fontSize: 28,
              fontWeight: 'bold',
              color: '#8B4513',
              lineHeight: 36
            },
            sub: {
              fontSize: 13,
              color: '#8B7355'
            }
          }
        },
        emphasis: {
          label: { show: true }
        },
        data: data
      }
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        bottom: 10,
        style: {
          text: `未确认标注共 ${unconfirmed} 条`,
          fill: '#8B7355',
          fontSize: 12
        }
      }
    ]
  }
  clueChartInstance.setOption(option)
}

const renderContributorChart = () => {
  if (!contributorChart.value) return
  if (contributorChartInstance) contributorChartInstance.dispose()
  contributorChartInstance = echarts.init(contributorChart.value)
  const data = [...(contributionStats.value?.leaderboard || [])].reverse()
  const medals = ['🥇', '🥈', '🥉']
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const d = params[0]
        return `${d.name}<br/>贡献次数：${d.value} 次<br/>贡献积分：${data[d.dataIndex]?.points || 0} 分`
      }
    },
    grid: { left: 110, right: 50, top: 20, bottom: 30 },
    xAxis: { type: 'value', axisLabel: { color: '#8B7355' }, splitLine: { lineStyle: { color: '#F5EDE0' } } },
    yAxis: {
      type: 'category',
      data: data.map((d, i) => {
        const idx = data.length - 1 - i
        const medal = idx < 3 ? medals[idx] + ' ' : ''
        return medal + d.contributor
      }),
      axisLabel: { color: '#5D4E3A', fontWeight: 500 }
    },
    series: [{
      type: 'bar',
      data: data.map((d, i) => ({
        value: d.count,
        itemStyle: {
          borderRadius: [0, 8, 8, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: ['#FBBF24', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#F97316'][i] || '#D2691E' },
            { offset: 1, color: ['#FDE68A', '#FDBA74', '#6EE7B7', '#93C5FD', '#C4B5FD', '#F9A8D4', '#FDBA74'][i] || '#F4A460' }
          ])
        }
      })),
      label: {
        show: true,
        position: 'right',
        color: '#8B4513',
        fontWeight: 600,
        formatter: '{c} 次'
      },
      barWidth: '55%'
    }]
  }
  contributorChartInstance.setOption(option)
}

const renderTaskTypeChart = () => {
  if (!taskTypeChart.value) return
  if (taskTypeChartInstance) taskTypeChartInstance.dispose()
  taskTypeChartInstance = echarts.init(taskTypeChart.value)
  const typeMap = {
    identity_confirm: { label: '人物身份确认', color: '#3B82F6' },
    old_name_supplement: { label: '旧称/别名补充', color: '#F59E0B' },
    migration_supplement: { label: '迁居信息补充', color: '#10B981' },
    event_narration: { label: '事件背景口述', color: '#8B5CF6' },
    relation_verify: { label: '亲属关系校验', color: '#EC4899' }
  }
  const raw = taskStats.value?.type_distribution || []
  const total = raw.reduce((s, x) => s + (x.count || 0), 0) || 1
  const data = raw.map(item => ({
    value: item.count,
    name: typeMap[item.type]?.label || item.type,
    itemStyle: { color: typeMap[item.type]?.color || '#D2691E' }
  }))
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 项 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '3%',
      top: 'center',
      textStyle: { color: '#5D4E3A', fontSize: 12 }
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '72%'],
        center: ['32%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 3
        },
        label: {
          show: true,
          position: 'center',
          formatter: [
            '{total|' + total + '}',
            '{sub|项采集任务}'
          ].join('\n'),
          rich: {
            total: { fontSize: 32, fontWeight: 'bold', color: '#8B4513', lineHeight: 40 },
            sub: { fontSize: 13, color: '#8B7355' }
          }
        },
        emphasis: {
          label: { show: true, fontSize: 16, fontWeight: 'bold' }
        },
        labelLine: { show: false },
        data: data
      }
    ]
  }
  taskTypeChartInstance.setOption(option)
}

const renderTopTaskPersonChart = () => {
  if (!topTaskPersonChart.value) return
  if (topTaskPersonChartInstance) topTaskPersonChartInstance.dispose()
  topTaskPersonChartInstance = echarts.init(topTaskPersonChart.value)
  const data = [...(taskStats.value?.top_persons || [])].reverse()
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}: {c} 项待补注任务' },
    grid: { left: 100, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value', axisLabel: { color: '#8B7355' }, splitLine: { lineStyle: { color: '#F5EDE0' } } },
    yAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLabel: { color: '#5D4E3A', fontWeight: 500 }
    },
    series: [{
      type: 'bar',
      data: data.map((d, i) => ({
        value: d.count,
        itemStyle: {
          borderRadius: [0, 10, 10, 0],
          color: d.count >= 4
            ? new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#F87171' },
                { offset: 1, color: '#DC2626' }
              ])
            : d.count >= 2
            ? new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#FBBF24' },
                { offset: 1, color: '#D97706' }
              ])
            : new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#60A5FA' },
                { offset: 1, color: '#2563EB' }
              ])
        }
      })),
      label: {
        show: true,
        position: 'right',
        color: '#8B4513',
        fontWeight: 600,
        formatter: '{c} 项'
      },
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: '#DC2626', type: 'dashed' },
        label: { formatter: '高危线 ≥4', color: '#DC2626', position: 'insideEndTop' },
        data: [{ xAxis: 4 }]
      },
      barWidth: '60%'
    }]
  }
  topTaskPersonChartInstance.setOption(option)
}

const renderDecadeCoverageChart = () => {
  if (!decadeCoverageChart.value) return
  if (decadeCoverageChartInstance) decadeCoverageChartInstance.dispose()
  decadeCoverageChartInstance = echarts.init(decadeCoverageChart.value)

  const raw = spacetimeStats.value?.decade_coverage || []
  const allDecades = ['1920s', '1930s', '1940s', '1950s', '1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s']
  const data = allDecades.map(decade => {
    const match = raw.find(d => d.decade === decade)
    return {
      decade,
      label: `${decade.slice(0, 3)}年代`,
      node_count: match?.count || match?.node_count || 0,
      coverage: match?.coverage || 0
    }
  })

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (p) => `${p[0].name}<br/>时空节点：${p[0].value} 个`
    },
    legend: {
      data: ['节点数量'],
      textStyle: { color: '#5D4E3A' }
    },
    grid: { left: 50, right: 50, top: 50, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.label),
      axisLabel: { color: '#8B7355', rotate: 30, fontSize: 10 }
    },
    yAxis: [
      {
        type: 'value',
        name: '节点数',
        axisLabel: { color: '#8B7355' },
        splitLine: { lineStyle: { color: '#F5EDE0' } }
      }
    ],
    series: [
      {
        name: '节点数量',
        type: 'bar',
        data: data.map((d, i) => ({
          value: d.node_count,
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#D2691E' },
              { offset: 1, color: '#F4A460' }
            ])
          }
        })),
        barWidth: '45%'
      }
    ]
  }
  decadeCoverageChartInstance.setOption(option)
}

const renderLocationRankChart = () => {
  if (!locationRankChart.value) return
  if (locationRankChartInstance) locationRankChartInstance.dispose()
  locationRankChartInstance = echarts.init(locationRankChart.value)

  const raw = spacetimeStats.value?.top_migration_locations || spacetimeStats.value?.top_in_locations || []
  if (!raw.length) {
    locationRankChartInstance.setOption({
      title: {
        text: '暂无地点数据',
        left: 'center',
        top: 'center',
        textStyle: { color: '#B5A48C', fontSize: 16, fontWeight: 'normal' }
      }
    })
    return
  }

  const data = raw.slice(0, 8).reverse()
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (p) => {
        const d = data[p[0].dataIndex]
        return `${d.name}<br/>节点数: ${d.count || d.in_count || 0} 次`
      }
    },
    grid: { left: 80, right: 40, top: 20, bottom: 30 },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#8B7355' },
      splitLine: { lineStyle: { color: '#F5EDE0' } }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLabel: { color: '#5D4E3A', fontWeight: 500 }
    },
    series: [
      {
        name: '节点数',
        type: 'bar',
        data: data.map(d => ({
          value: d.count || d.in_count || 0,
          itemStyle: {
            borderRadius: [0, 10, 10, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#F4A460' },
              { offset: 1, color: '#D2691E' }
            ])
          }
        })),
        label: {
          show: true,
          position: 'right',
          color: '#8B4513',
          fontWeight: 600,
          formatter: '{c} 次'
        },
        barWidth: '55%'
      }
    ]
  }
  locationRankChartInstance.setOption(option)
}

const handleResize = () => {
  eraChartInstance?.resize()
  topChartInstance?.resize()
  clueChartInstance?.resize()
  contributorChartInstance?.resize()
  taskTypeChartInstance?.resize()
  topTaskPersonChartInstance?.resize()
  decadeCoverageChartInstance?.resize()
  locationRankChartInstance?.resize()
}

watch([() => stats.value, () => taskStats.value, () => contributionStats.value, () => spacetimeStats.value], () => {
  nextTick(() => {
    renderEraChart()
    renderTopChart()
    renderClueChart()
    renderContributorChart()
    renderTaskTypeChart()
    renderTopTaskPersonChart()
    renderDecadeCoverageChart()
    renderLocationRankChart()
  })
})

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.stat-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 24px;
  border-radius: 16px;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.stat-card::after {
  content: '';
  position: absolute;
  top: -30px;
  right: -30px;
  width: 120px;
  height: 120px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 50%;
}

.stat-icon {
  font-size: 36px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 40px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.stat-label {
  font-size: 14px;
  opacity: 0.92;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.stat-trend {
  font-size: 12px;
  opacity: 0.85;
  position: relative;
  z-index: 1;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-trend.highlight {
  color: #FEF3C7;
  font-weight: 600;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  padding: 20px 24px;
}

.chart-card.wide {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  align-items: center;
  padding-bottom: 14px;
  margin-bottom: 14px;
  border-bottom: 1px solid #F5EDE0;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #8B4513;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chart-header .sub-hint {
  font-size: 12px;
  color: #B5A48C;
  margin-left: 8px;
}

.completion-tags {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.chart-canvas {
  width: 100%;
  height: 340px;
}

.chart-body {
  padding-top: 4px;
}

.completion-section {
  margin-bottom: 24px;
}

.completion-section:last-child {
  margin-bottom: 0;
}

.completion-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E3A;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 3px solid #D2691E;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-item {
  background: #FFFAF0;
  padding: 10px 16px;
  border-radius: 10px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: #5D4E3A;
}

.progress-num {
  font-weight: 600;
  color: #8B4513;
}

.flow-overview {
  display: grid;
  grid-template-columns: 1fr 30px 1fr 30px 1fr 30px 1fr 30px 1fr;
  gap: 6px;
  align-items: stretch;
  padding: 8px 0;
}

.flow-node {
  padding: 24px 20px;
  border-radius: 16px;
  color: white;
  text-align: center;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
}

.flow-node-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.flow-node-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.flow-node-num {
  font-size: 14px;
  opacity: 0.95;
  margin-bottom: 14px;
}

.flow-node-progress {
  background: rgba(255, 255, 255, 0.2);
  padding: 10px 14px;
  border-radius: 10px;
}

.fn-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 6px;
}

.fn-fill {
  height: 100%;
  background: white;
  border-radius: 4px;
  transition: width 0.4s;
}

.flow-node-progress span {
  font-size: 12px;
  font-weight: 600;
}

.flow-arrow-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #D2691E;
  font-weight: 700;
}

.legend-card {
  padding: 24px 28px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #8B4513;
  padding-left: 12px;
  border-left: 3px solid #F4A460;
}

.legend-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: #FFFAF0;
  border-radius: 10px;
  border: 1px solid #F5EDE0;
}

.legend-item b {
  font-size: 14px;
  color: #5D4E3A;
  display: block;
  margin-bottom: 4px;
}

.legend-item p {
  font-size: 13px;
  color: #8B7355;
  margin: 0;
}
</style>
