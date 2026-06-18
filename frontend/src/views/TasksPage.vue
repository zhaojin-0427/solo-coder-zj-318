<template>
  <div class="tasks-page">
    <div class="page-header">
      <div class="page-title">
        <el-icon><List /></el-icon>
        采集任务中心
      </div>
      <div class="page-subtitle">围绕家属贡献人的任务分派、认领、提交与审核，系统化采集家族记忆的每一个片段</div>
    </div>

    <div class="stats-overview" v-loading="statsLoading">
      <div class="ov-card ov-blue">
        <div class="ov-icon">📋</div>
        <div class="ov-num">{{ taskStats?.open_tasks || 0 }}</div>
        <div class="ov-label">待完成任务</div>
        <div class="ov-desc">含已分派和待认领</div>
      </div>
      <div class="ov-card ov-orange">
        <div class="ov-icon">✍️</div>
        <div class="ov-num">{{ taskStats?.in_progress_tasks || 0 }}</div>
        <div class="ov-label">处理中任务</div>
        <div class="ov-desc">正在补注中</div>
      </div>
      <div class="ov-card ov-purple">
        <div class="ov-icon">🔍</div>
        <div class="ov-num">{{ taskStats?.submitted_tasks || 0 }}</div>
        <div class="ov-label">待审核提交</div>
        <div class="ov-desc">等待审核通过</div>
      </div>
      <div class="ov-card ov-green">
        <div class="ov-icon">✅</div>
        <div class="ov-num">{{ taskStats?.completion_rate || 0 }}%</div>
        <div class="ov-label">任务完成率</div>
        <div class="ov-desc">已完成 / 已关闭</div>
      </div>
      <div class="ov-card ov-red">
        <div class="ov-icon">⚖️</div>
        <div class="ov-num">{{ taskStats?.conflict_rate || 0 }}%</div>
        <div class="ov-label">冲突转确认率</div>
        <div class="ov-desc">提交后需家庭投票</div>
      </div>
    </div>

    <div class="layout-row">
      <div class="main-panel">
        <div class="panel-card card-warm">
          <div class="panel-header">
            <el-tabs v-model="activeTab" @tab-change="onTabChange">
              <el-tab-pane label="全部任务" name="all">
                <template #label>
                  <span><el-icon><Document /></el-icon> 全部任务 ({{ totalAll }})</span>
                </template>
              </el-tab-pane>
              <el-tab-pane label="我的贡献" name="mine">
                <template #label>
                  <span><el-icon><UserFilled /></el-icon> 我的贡献</span>
                </template>
              </el-tab-pane>
              <el-tab-pane label="贡献排行" name="ranking">
                <template #label>
                  <span><el-icon><Trophy /></el-icon> 贡献排行</span>
                </template>
              </el-tab-pane>
            </el-tabs>
            <div class="header-actions">
              <el-button :icon="MagicStick" type="warning" @click="showGenerate = true">
                智能生成任务
              </el-button>
              <el-button :icon="Plus" type="primary" @click="openCreateTask">
                新建任务
              </el-button>
            </div>
          </div>

          <div v-if="activeTab === 'all'" class="filter-bar">
            <el-select v-model="filterType" placeholder="任务类型" clearable style="width: 180px">
              <el-option v-for="opt in TASK_TYPE_OPTIONS" :key="opt.value"
                :label="opt.label" :value="opt.value" />
            </el-select>
            <el-select v-model="filterSource" placeholder="来源类型" clearable style="width: 140px">
              <el-option v-for="opt in TASK_SOURCE_OPTIONS" :key="opt.value"
                :label="opt.label" :value="opt.value" />
            </el-select>
            <el-select v-model="filterStatus" placeholder="任务状态" clearable style="width: 140px">
              <el-option v-for="opt in TASK_STATUS_OPTIONS" :key="opt.value"
                :label="opt.label" :value="opt.value" />
            </el-select>
            <el-select v-model="filterAssign" placeholder="分派方式" clearable style="width: 140px">
              <el-option v-for="opt in TASK_ASSIGN_OPTIONS" :key="opt.value"
                :label="opt.label" :value="opt.value" />
            </el-select>
            <el-input v-model="searchKey" placeholder="搜索标题/描述"
              style="width: 220px" clearable :prefix-icon="Search" />
            <el-button :icon="Refresh" @click="loadTasks">刷新</el-button>
          </div>

          <div v-if="activeTab === 'all'" class="task-list" v-loading="loading">
            <div v-if="tasks.length === 0" class="empty-state">
              <el-empty description="暂无任务，点击「智能生成任务」或「新建任务」开始">
                <el-button type="primary" @click="showGenerate = true">生成任务</el-button>
              </el-empty>
            </div>
            <div v-else>
              <div v-for="task in tasks" :key="task.id" class="task-card" @click="openTaskDetail(task)">
                <div class="task-left">
                  <div class="task-type-badge" :style="{ background: getTaskTypeInfo(task.task_type).color + '20', color: getTaskTypeInfo(task.task_type).color, borderColor: getTaskTypeInfo(task.task_type).color }">
                    <el-icon><component :is="getTaskTypeInfo(task.task_type).icon" /></el-icon>
                    <span>{{ task.task_type_display }}</span>
                  </div>
                  <div class="task-title">{{ task.title }}</div>
                  <div class="task-desc">{{ task.description || '无详细描述' }}</div>
                  <div class="task-meta">
                    <el-tag size="small" :type="getTaskStatusInfo(task.status).type" effect="light">
                      {{ task.status_display }}
                    </el-tag>
                    <span class="meta-item">
                      <el-icon><component :is="getTaskSourceInfo(task.source_type).icon" /></el-icon>
                      {{ task.source_type_display }}
                    </span>
                    <span v-if="task.related_person_detail" class="meta-item">
                      <el-avatar size="small" :style="{ background: '#D2691E' }">
                        {{ task.related_person_detail.name?.charAt(0) }}
                      </el-avatar>
                      {{ task.related_person_detail.name }}
                    </span>
                    <span v-if="task.related_photo_detail" class="meta-item">
                      🖼️ {{ task.related_photo_detail.title || '照片#' + task.related_photo }}
                    </span>
                    <span v-if="task.related_memory_title" class="meta-item">
                      📜 {{ task.related_memory_title }}
                    </span>
                    <span class="meta-item">{{ task.assign_type_display }}</span>
                    <span v-if="task.assigned_to" class="meta-item highlight-assign">
                      指派: {{ task.assigned_to }}
                    </span>
                    <span v-if="task.claimed_by" class="meta-item highlight-claim">
                      认领: {{ task.claimed_by }}
                    </span>
                    <span class="meta-item">{{ formatTime(task.created_at) }}</span>
                  </div>
                </div>
                <div class="task-right">
                  <el-button v-if="task.status === 'open' || task.status === 'assigned'"
                    type="primary" :icon="Check" size="small"
                    @click.stop="claimTask(task)">认领任务</el-button>
                  <el-button v-else-if="task.status === 'in_progress' && task.claimed_by === CURRENT_USER"
                    type="warning" :icon="Edit" size="small"
                    @click.stop="openSubmit(task)">提交补注</el-button>
                  <el-button v-else-if="task.status === 'submitted'"
                    type="success" :icon="Promotion" size="small"
                    @click.stop="openReview(task)">审核</el-button>
                  <el-button v-else type="info" :icon="View" size="small"
                    @click.stop="openTaskDetail(task)">查看详情</el-button>
                </div>
              </div>
              <div class="pagination-wrap">
                <el-pagination
                  background
                  layout="prev, pager, next"
                  :total="totalAll"
                  :page-size="pageSize"
                  :current-page="currentPage"
                  @current-change="onPageChange"
                />
              </div>
            </div>
          </div>

          <div v-if="activeTab === 'mine'" class="my-contribution" v-loading="statsLoading">
            <div class="my-stats-grid">
              <div class="my-stat-card">
                <div class="my-stat-icon" style="background: linear-gradient(135deg,#667EEA,#764BA2);">
                  🏆
                </div>
                <div class="my-stat-info">
                  <div class="my-stat-num">{{ myContribution?.total_points || 0 }}</div>
                  <div class="my-stat-label">累计贡献积分</div>
                </div>
              </div>
              <div class="my-stat-card">
                <div class="my-stat-icon" style="background: linear-gradient(135deg,#F59E0B,#D97706);">
                  📋
                </div>
                <div class="my-stat-info">
                  <div class="my-stat-num">{{ myContribution?.total_count || 0 }}</div>
                  <div class="my-stat-label">贡献次数</div>
                </div>
              </div>
              <div class="my-stat-card">
                <div class="my-stat-icon" style="background: linear-gradient(135deg,#10B981,#059669);">
                  ✅
                </div>
                <div class="my-stat-info">
                  <div class="my-stat-num">{{ myApprovedTasks }}</div>
                  <div class="my-stat-label">已完成任务</div>
                </div>
              </div>
              <div class="my-stat-card">
                <div class="my-stat-icon" style="background: linear-gradient(135deg,#EF4444,#DC2626);">
                  ⏳
                </div>
                <div class="my-stat-info">
                  <div class="my-stat-num">{{ myInProgressTasks }}</div>
                  <div class="my-stat-label">进行中任务</div>
                </div>
              </div>
            </div>

            <div class="section-block">
              <h4 class="section-title"><el-icon><TrendCharts /></el-icon> 我的贡献分布</h4>
              <div ref="myContribChart" class="chart-area"></div>
            </div>

            <div class="section-block">
              <h4 class="section-title"><el-icon><List /></el-icon> 我的任务记录</h4>
              <el-table :data="myTasks" stripe style="width: 100%" v-loading="loading">
                <el-table-column prop="task_type_display" label="任务类型" width="140">
                  <template #default="{ row }">
                    <el-tag size="small" effect="light"
                      :style="{ color: getTaskTypeInfo(row.task_type).color, borderColor: getTaskTypeInfo(row.task_type).color + '50', background: getTaskTypeInfo(row.task_type).color + '10' }">
                      {{ row.task_type_display }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="title" label="任务标题" show-overflow-tooltip />
                <el-table-column prop="status_display" label="状态" width="120">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getTaskStatusInfo(row.status).type">
                      {{ row.status_display }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="claimed_at" label="认领时间" width="170">
                  <template #default="{ row }">{{ formatTime(row.claimed_at) }}</template>
                </el-table-column>
                <el-table-column label="操作" width="160" fixed="right">
                  <template #default="{ row }">
                    <el-button type="primary" link size="small" @click="openTaskDetail(row)">详情</el-button>
                    <el-button v-if="row.status === 'in_progress' && row.claimed_by === CURRENT_USER"
                      type="warning" link size="small" @click="openSubmit(row)">提交</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div class="section-block">
              <h4 class="section-title"><el-icon><Clock /></el-icon> 最近贡献动态</h4>
              <div class="contrib-timeline">
                <div v-for="(c, idx) in (myContribution?.recent || [])" :key="c.id || idx" class="timeline-item">
                  <div class="timeline-dot" :style="{ background: getContribColor(c.contribution_type) }"></div>
                  <div class="timeline-content">
                    <div class="timeline-top">
                      <span class="timeline-type">{{ getContribLabel(c.contribution_type) }}</span>
                      <span class="timeline-time">{{ formatTime(c.created_at) }}</span>
                    </div>
                    <div class="timeline-desc">{{ c.description || '贡献记录' }}</div>
                    <div class="timeline-points">+{{ c.points }} 积分</div>
                  </div>
                </div>
                <div v-if="!(myContribution?.recent || []).length" class="empty-timeline">
                  暂无贡献记录，快去认领任务吧！
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeTab === 'ranking'" class="ranking-panel" v-loading="statsLoading">
            <div class="ranking-list">
              <div v-for="(item, idx) in (taskStats?.contribution_leaderboard || [])"
                :key="item.contributor"
                class="rank-item" :class="{ 'rank-me': item.contributor === CURRENT_USER }">
                <div class="rank-pos" :class="'rank-' + (idx + 1)">
                  {{ idx < 3 ? ['🥇', '🥈', '🥉'][idx] : idx + 1 }}
                </div>
                <div class="rank-avatar" :style="{ background: rankColors[idx % rankColors.length] }">
                  {{ item.contributor?.charAt(0) || '?' }}
                </div>
                <div class="rank-info">
                  <div class="rank-name">
                    {{ item.contributor }}
                    <el-tag v-if="item.contributor === CURRENT_USER" size="small" type="warning" effect="dark">我</el-tag>
                  </div>
                  <div class="rank-stats">
                    <span>任务 {{ item.task_count || 0 }} 个</span>
                    <span>审核通过 {{ item.task_approved_count || 0 }} 次</span>
                  </div>
                </div>
                <div class="rank-points">
                  <div class="points-num">{{ item.total_points || 0 }}</div>
                  <div class="points-label">积分</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="side-panel">
        <div class="panel-card card-warm">
          <h3 class="side-title"><el-icon><Connection /></el-icon> 高频待补注人物 TOP</h3>
          <div class="side-list">
            <div v-for="(p, idx) in (taskStats?.top_task_persons || []).slice(0, 8)"
              :key="p.person_id" class="side-item">
              <div class="side-rank">{{ idx + 1 }}</div>
              <div class="side-info">
                <div class="side-name">{{ p.name }}</div>
                <el-progress
                  :percentage="Math.min(100, (p.task_count || 0) * 10)"
                  :stroke-width="10"
                  :show-text="false"
                  color="#D2691E"
                />
              </div>
              <div class="side-count">{{ p.task_count }} 项</div>
            </div>
            <el-empty v-if="!taskStats?.top_task_persons?.length" description="暂无数据" :image-size="80" />
          </div>
        </div>

        <div class="panel-card card-warm">
          <h3 class="side-title"><el-icon><PieChart /></el-icon> 任务类型分布</h3>
          <div ref="typeChart" class="chart-area" style="height: 260px;"></div>
        </div>
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="任务详情" width="780px" destroy-on-close>
      <div v-if="currentTask" class="task-detail">
        <div class="detail-head">
          <div class="task-type-badge lg" :style="{ background: getTaskTypeInfo(currentTask.task_type).color + '20', color: getTaskTypeInfo(currentTask.task_type).color, borderColor: getTaskTypeInfo(currentTask.task_type).color }">
            <el-icon><component :is="getTaskTypeInfo(currentTask.task_type).icon" /></el-icon>
            <span>{{ currentTask.task_type_display }}</span>
          </div>
          <el-tag :type="getTaskStatusInfo(currentTask.status).type" size="large">
            {{ currentTask.status_display }}
          </el-tag>
        </div>
        <h2 class="detail-title">{{ currentTask.title }}</h2>
        <p class="detail-desc">{{ currentTask.description }}</p>

        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="来源类型">{{ currentTask.source_type_display }}</el-descriptions-item>
          <el-descriptions-item label="分派方式">{{ currentTask.assign_type_display }}</el-descriptions-item>
          <el-descriptions-item label="指派对象">{{ currentTask.assigned_to || '全家开放' }}</el-descriptions-item>
          <el-descriptions-item label="认领人">{{ currentTask.claimed_by || '尚未认领' }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ currentTask.created_by }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentTask.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="关联照片" v-if="currentTask.related_photo_detail">
            <span>🖼️ {{ currentTask.related_photo_detail.title || '#' + currentTask.related_photo }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="关联人物" v-if="currentTask.related_person_detail">
            <span>👤 {{ currentTask.related_person_detail.name }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="关联回忆" v-if="currentTask.related_memory_title">
            <span>📜 {{ currentTask.related_memory_title }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag v-if="currentTask.priority >= 10" type="danger">高</el-tag>
            <el-tag v-else-if="currentTask.priority >= 5" type="warning">中</el-tag>
            <el-tag v-else type="info">普通</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4><el-icon><ChatDotRound /></el-icon> 任务补注提交记录</h4>
          <div v-if="submissions.length" class="submission-list">
            <div v-for="sub in submissions" :key="sub.id" class="sub-item">
              <div class="sub-head">
                <el-avatar :size="32" style="background:#D2691E">{{ sub.submitter?.charAt(0) }}</el-avatar>
                <div class="sub-meta">
                  <div class="sub-user">{{ sub.submitter }}</div>
                  <div class="sub-time">{{ formatTime(sub.created_at) }}</div>
                </div>
                <el-tag :type="getSubStatusType(sub.status)">{{ sub.status_display }}</el-tag>
              </div>
              <div v-if="sub.submission_text" class="sub-text">{{ sub.submission_text }}</div>
              <div v-if="Object.keys(sub.submission_data || {}).length" class="sub-data">
                <div v-for="(v, k) in sub.submission_data" :key="k" class="data-row">
                  <span class="data-key">{{ getFieldLabel(k) }}:</span>
                  <span class="data-val">{{ v }}</span>
                </div>
              </div>
              <div v-if="sub.has_conflict" class="sub-conflict">
                <el-icon><WarningFilled /></el-icon>
                <span>冲突: {{ sub.conflict_description }}</span>
              </div>
              <div v-if="sub.review_comment" class="sub-review">
                <div class="review-label">审核意见 ({{ sub.reviewer }}):</div>
                <div class="review-text">{{ sub.review_comment }}</div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无提交记录" :image-size="80" />
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button v-if="currentTask.status === 'open' || currentTask.status === 'assigned'"
            type="primary" @click="claimTask(currentTask)">认领任务</el-button>
          <el-button v-else-if="currentTask.status === 'in_progress' && currentTask.claimed_by === CURRENT_USER"
            type="warning" @click="openSubmit(currentTask)">提交补注</el-button>
          <el-button v-else-if="currentTask.status === 'submitted'"
            type="success" @click="openReview(currentTask)">审核提交</el-button>
          <el-button @click="detailVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="submitVisible" title="提交任务补注" width="640px" destroy-on-close>
      <div v-if="currentTask" class="submit-form">
        <div class="form-hint">
          <el-alert
            :title="'任务类型：' + currentTask.task_type_display"
            type="info"
            :closable="false"
            show-icon
          />
        </div>

        <template v-if="currentTask.task_type === 'identity_confirm'">
          <el-form-item label="确认身份">
            <el-select v-model="submitData.person_id" placeholder="选择关联的人物档案" filterable style="width: 100%">
              <el-option v-for="p in allPersons" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="位置说明">
            <el-input v-model="submitData.position_note" placeholder="如：前排左一、后排中间等" />
          </el-form-item>
        </template>

        <template v-else-if="currentTask.task_type === 'old_name_supplement'">
          <el-form-item label="别名/旧称" required>
            <el-input v-model="submitData.alias_name" placeholder="乳名、曾用名、旧时称呼等" />
          </el-form-item>
          <el-form-item label="使用场景">
            <el-input v-model="submitData.usage_context" placeholder="如：家里人叫的乳名、工作单位用名等" />
          </el-form-item>
        </template>

        <template v-else-if="currentTask.task_type === 'migration_supplement'">
          <el-form-item label="迁出地" required>
            <el-input v-model="submitData.from_place" placeholder="原居住地" />
          </el-form-item>
          <el-form-item label="迁入地" required>
            <el-input v-model="submitData.to_place" placeholder="迁居后地点" />
          </el-form-item>
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item label="迁居年份">
                <el-input-number v-model="submitData.move_year" :min="1800" :max="2100" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="迁居原因">
                <el-input v-model="submitData.reason" placeholder="如：工作调动、逃荒、婚嫁等" />
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <template v-else-if="currentTask.task_type === 'event_narration'">
          <el-form-item label="事件描述" required>
            <el-input type="textarea" v-model="submitData.description" :rows="5"
              placeholder="请详细记录老人口述的事件背景、发生的故事、感人细节等" />
          </el-form-item>
          <el-form-item label="额外口述内容">
            <el-input type="textarea" v-model="submitFormText" :rows="4"
              placeholder="可以补充更多故事细节..." />
          </el-form-item>
        </template>

        <template v-else-if="currentTask.task_type === 'relation_verify'">
          <el-form-item label="对方人物">
            <el-select v-model="submitData.to_person_id" placeholder="选择关联的亲属" filterable style="width: 100%">
              <el-option v-for="p in allPersons" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="亲属关系">
            <el-select v-model="submitData.relation_type" placeholder="选择关系类型" style="width: 100%">
              <el-option v-for="opt in RELATION_OPTIONS" :key="opt.value"
                :label="opt.label" :value="opt.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="关系备注">
            <el-input v-model="submitData.relation_note" placeholder="如：大舅、二伯母等具体说明" />
          </el-form-item>
        </template>
      </div>
      <template #footer>
        <el-button @click="submitVisible = false">取消</el-button>
        <el-button type="primary" @click="doSubmit">提交补注</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="reviewVisible" title="审核任务提交" width="640px" destroy-on-close>
      <div v-if="currentTask && latestSubmission" class="review-form">
        <div class="review-head">
          <div class="review-user">
            <el-avatar :size="40" style="background:#D2691E">{{ latestSubmission.submitter?.charAt(0) }}</el-avatar>
            <div>
              <div class="review-name">{{ latestSubmission.submitter }} 的提交</div>
              <div class="review-time">{{ formatTime(latestSubmission.created_at) }}</div>
            </div>
          </div>
          <el-tag v-if="latestSubmission.has_conflict" type="danger" effect="dark">检测到冲突</el-tag>
        </div>

        <div class="review-content">
          <div v-if="latestSubmission.submission_text" class="review-block">
            <label>口述内容：</label>
            <div class="review-text-block">{{ latestSubmission.submission_text }}</div>
          </div>
          <div v-if="Object.keys(latestSubmission.submission_data || {}).length" class="review-block">
            <label>结构化数据：</label>
            <div class="data-table">
              <div v-for="(v, k) in latestSubmission.submission_data" :key="k" class="data-row">
                <span class="data-key">{{ getFieldLabel(k) }}</span>
                <span class="data-val">{{ v }}</span>
              </div>
            </div>
          </div>
          <div v-if="latestSubmission.conflict_description" class="review-block conflict">
            <el-icon><WarningFilled /></el-icon>
            <span>{{ latestSubmission.conflict_description }}</span>
          </div>
        </div>

        <el-form-item label="审核意见">
          <el-input type="textarea" v-model="reviewComment" :rows="3" placeholder="请填写审核意见（可选）" />
        </el-form-item>
      </div>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="danger" @click="doReview('to_conflict')">转家庭确认台</el-button>
        <el-button type="warning" @click="doReview('reject')">驳回</el-button>
        <el-button type="success" @click="doReview('approve')">审核通过</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showGenerate" title="智能生成采集任务" width="680px" destroy-on-close>
      <div class="gen-form">
        <el-alert type="warning" show-icon :closable="false"
          title="系统将基于现有资料自动生成待补注任务"
          description="按照片、人物、回忆片段的缺失信息维度，批量创建标准化补注任务"
          style="margin-bottom: 20px;" />
        <el-form label-width="110px">
          <el-form-item label="生成来源">
            <el-radio-group v-model="genForm.source_type">
              <el-radio value="photo">仅照片</el-radio>
              <el-radio value="person">仅人物</el-radio>
              <el-radio value="memory">仅回忆</el-radio>
              <el-radio value="all">全部类型</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="任务类型">
            <el-checkbox-group v-model="genForm.task_types">
              <el-checkbox v-for="opt in TASK_TYPE_OPTIONS" :key="opt.value"
                :label="opt.value">{{ opt.label }}</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="分派方式">
            <el-radio-group v-model="genForm.assign_type">
              <el-radio value="family">全家开放认领</el-radio>
              <el-radio value="specific">指定人员</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item v-if="genForm.assign_type === 'specific'" label="指定分派">
            <el-input v-model="genForm.assigned_to" placeholder="填写家属姓名，如：王秀兰" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showGenerate = false">取消</el-button>
        <el-button type="primary" @click="doGenerate">开始生成任务</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  List, Document, UserFilled, Trophy, MagicStick, Plus, Search, Refresh,
  Check, Edit, View, Promotion, TrendCharts, Clock, PieChart,
  ChatDotRound, Connection, WarningFilled
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { tasks as tasksApi, persons as personsApi } from '@/api'
import {
  TASK_TYPE_OPTIONS, TASK_SOURCE_OPTIONS, TASK_STATUS_OPTIONS, TASK_ASSIGN_OPTIONS,
  SUBMISSION_STATUS_OPTIONS, CONTRIBUTION_TYPE_OPTIONS, CURRENT_USER, RELATION_OPTIONS,
  getTaskTypeInfo, getTaskStatusInfo, getOptionLabel
} from '@/store'

const route = useRoute()
const loading = ref(false)
const statsLoading = ref(false)
const tasks = ref([])
const taskStats = ref({})
const myContribution = ref({})
const allPersons = ref([])
const activeTab = ref('all')
const filterType = ref('')
const filterSource = ref('')
const filterStatus = ref('')
const filterAssign = ref('')
const filterRelatedId = ref('')
const searchKey = ref('')
const currentPage = ref(1)
const pageSize = 10
const totalAll = ref(0)

const myTasks = computed(() => {
  return tasks.value.filter(t => t.claimed_by === CURRENT_USER || t.assigned_to === CURRENT_USER)
})
const myApprovedTasks = computed(() => myTasks.value.filter(t => t.status === 'completed').length)
const myInProgressTasks = computed(() => myTasks.value.filter(t => ['in_progress', 'assigned', 'submitted'].includes(t.status)).length)

const detailVisible = ref(false)
const submitVisible = ref(false)
const reviewVisible = ref(false)
const showGenerate = ref(false)
const currentTask = ref(null)
const submissions = ref([])
const latestSubmission = ref(null)
const submitData = ref({})
const submitFormText = ref('')
const reviewComment = ref('')
const genForm = ref({
  source_type: 'all',
  task_types: [],
  assign_type: 'family',
  assigned_to: ''
})

const rankColors = ['#D2691E', '#C0392B', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#06B6D4']
const myContribChart = ref(null)
const typeChart = ref(null)
let myChartInstance = null
let typeChartInstance = null

const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-') : '-'
const getTaskSourceInfo = (v) => TASK_SOURCE_OPTIONS.find(o => o.value === v) || TASK_SOURCE_OPTIONS[0]
const getSubStatusType = (v) => (SUBMISSION_STATUS_OPTIONS.find(o => o.value === v) || {}).type || 'info'
const getContribLabel = (v) => (CONTRIBUTION_TYPE_OPTIONS.find(o => o.value === v) || {}).label || v
const getContribColor = (v) => (CONTRIBUTION_TYPE_OPTIONS.find(o => o.value === v) ? '#D2691E' : '#8B7355')
const getFieldLabel = (k) => ({
  person_id: '关联人物ID',
  position_note: '位置说明',
  alias_name: '别名/旧称',
  usage_context: '使用场景',
  from_place: '迁出地',
  to_place: '迁入地',
  move_year: '迁居年份',
  reason: '迁居原因',
  description: '事件描述',
  content: '内容',
  to_person_id: '对方人物ID',
  relation_type: '亲属关系',
  relation_note: '关系备注'
}[k] || k)

const onTabChange = () => {
  if (activeTab.value === 'all') loadTasks()
  if (activeTab.value === 'mine') {
    loadTaskStats()
    nextTick(() => renderMyContribChart())
  }
  if (activeTab.value === 'ranking') {
    loadTaskStats()
  }
}

const loadTasks = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filterType.value) params.task_type = filterType.value
    if (filterSource.value) params.source_type = filterSource.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterAssign.value) params.assign_type = filterAssign.value
    if (filterRelatedId.value && filterSource.value) {
      const fieldMap = { photo: 'related_photo', person: 'related_person', memory: 'related_memory' }
      const field = fieldMap[filterSource.value]
      if (field) params[field] = filterRelatedId.value
    }
    const res = await tasksApi.list(params)
    let list = res.results || res.data || []
    if (searchKey.value) {
      const key = searchKey.value.toLowerCase()
      list = list.filter(t =>
        (t.title || '').toLowerCase().includes(key) ||
        (t.description || '').toLowerCase().includes(key)
      )
    }
    tasks.value = list
    totalAll.value = res.count || list.length
  } catch (e) {
    console.error(e)
    mockTasks()
  } finally {
    loading.value = false
  }
}

const loadTaskStats = async () => {
  statsLoading.value = true
  try {
    const res = await tasksApi.stats({ contributor: CURRENT_USER })
    taskStats.value = res
    myContribution.value = res.my_contribution || {}
    nextTick(() => renderTypeChart())
  } catch (e) {
    console.error(e)
    taskStats.value = {
      total_tasks: 35,
      open_tasks: 12,
      assigned_tasks: 3,
      in_progress_tasks: 5,
      submitted_tasks: 4,
      completed_tasks: 10,
      rejected_tasks: 1,
      conflicted_tasks: 3,
      completion_rate: 71.4,
      conflict_rate: 23.1,
      total_submissions: 26,
      approved_submissions: 18,
      contribution_leaderboard: [
        { contributor: '王秀兰', total_points: 450, task_count: 15, task_approved_count: 12 },
        { contributor: '李建国', total_points: 380, task_count: 12, task_approved_count: 10 },
        { contributor: '张桂芬', total_points: 320, task_count: 10, task_approved_count: 8 },
        { contributor: CURRENT_USER, total_points: 280, task_count: 9, task_approved_count: 7 },
        { contributor: '李建华', total_points: 210, task_count: 7, task_approved_count: 6 },
        { contributor: '李建梅', total_points: 180, task_count: 6, task_approved_count: 5 },
      ],
      top_task_persons: [
        { person_id: 1, name: '李大山', task_count: 8 },
        { person_id: 2, name: '王秀兰', task_count: 7 },
        { person_id: 3, name: '李建国', task_count: 6 },
        { person_id: 4, name: '李建华', task_count: 5 },
        { person_id: 5, name: '李建梅', task_count: 4 },
        { person_id: 6, name: '张桂芬', task_count: 4 },
      ],
      task_type_distribution: [
        { type: 'identity_confirm', type_display: '人物身份确认', count: 10, completed: 6 },
        { type: 'old_name_supplement', type_display: '旧称/别名补充', count: 8, completed: 3 },
        { type: 'migration_supplement', type_display: '迁居信息补充', count: 5, completed: 2 },
        { type: 'event_narration', type_display: '事件背景口述', count: 7, completed: 5 },
        { type: 'relation_verify', type_display: '亲属关系校验', count: 5, completed: 2 },
      ],
      my_contribution: {
        contributor: CURRENT_USER,
        total_points: 280,
        total_count: 18,
        by_type: [
          { contribution_type: 'task_approved', count: 7, points: 210 },
          { contribution_type: 'task_submit', count: 9, points: 90 },
          { contribution_type: 'task_claim', count: 10, points: 50 },
          { contribution_type: 'review_pass', count: 2, points: 40 },
        ],
        recent: [
          { id: 1, contribution_type: 'task_approved', description: '任务补注审核通过：确认照片人物身份', points: 30, created_at: '2024-01-15 14:30:00' },
          { id: 2, contribution_type: 'task_submit', description: '提交任务补注：补充迁居信息-李大山', points: 10, created_at: '2024-01-15 10:20:00' },
          { id: 3, contribution_type: 'task_claim', description: '认领任务：记录事件背景口述-全家福', points: 5, created_at: '2024-01-14 16:00:00' },
        ]
      }
    }
    myContribution.value = taskStats.value.my_contribution
    nextTick(() => {
      renderTypeChart()
      if (activeTab.value === 'mine') renderMyContribChart()
    })
  } finally {
    statsLoading.value = false
  }
}

const loadPersons = async () => {
  try {
    const res = await personsApi.simple()
    allPersons.value = res || []
  } catch (e) {
    allPersons.value = []
  }
}

const mockTasks = () => {
  const mock = []
  const types = TASK_TYPE_OPTIONS.map(o => o.value)
  const statuses = ['open', 'assigned', 'in_progress', 'submitted', 'completed', 'conflicted']
  for (let i = 1; i <= 15; i++) {
    const tt = types[i % 5]
    const st = statuses[i % 7]
    mock.push({
      id: i,
      task_type: tt,
      task_type_display: getTaskTypeInfo(tt).label,
      title: ['确认人物身份：二舅在婚礼合影中的位置',
        '补充旧称：李大山的乳名叫什么？',
        '补充迁居信息：1968年王秀兰从哪里嫁到李家？',
        '事件背景口述：1978年春节全家福背后的故事',
        '校验亲属关系：张桂芬和李建国是什么关系？'][i % 5] + ' #' + i,
      description: '请根据老人口述或家族资料，认真完成此补注任务。如有多个版本请详细记录。',
      source_type: ['photo', 'person', 'memory'][i % 3],
      source_type_display: ['照片', '人物', '回忆片段'][i % 3],
      status: st,
      status_display: getTaskStatusInfo(st).label,
      assign_type: i % 3 === 0 ? 'specific' : 'family',
      assign_type_display: i % 3 === 0 ? '指定人员' : '全家开放',
      assigned_to: i % 3 === 0 ? '王秀兰' : '',
      claimed_by: ['in_progress', 'submitted', 'completed'].includes(st) ? (i % 2 === 0 ? CURRENT_USER : '王秀兰') : '',
      claimed_at: ['in_progress', 'submitted', 'completed'].includes(st) ? '2024-01-14 10:00:00' : null,
      related_person: i % 3 === 1 ? i : null,
      related_person_detail: i % 3 === 1 ? { id: i, name: '李大山' } : null,
      related_photo: i % 3 === 0 ? i : null,
      related_photo_detail: i % 3 === 0 ? { id: i, title: '1978年春节全家福' } : null,
      related_memory_title: i % 3 === 2 ? '那年夏天的海边之旅' : null,
      priority: i > 10 ? 10 : 5,
      created_by: '系统',
      created_at: '2024-01-10 09:00:00',
      submission_count: i % 3
    })
  }
  tasks.value = mock
  totalAll.value = mock.length
}

const openTaskDetail = async (task) => {
  currentTask.value = task
  submissions.value = []
  try {
    const res = await tasksApi.submissions(task.id)
    submissions.value = res || []
  } catch (e) {
    submissions.value = task.submission_count ? [
      {
        id: 1, submitter: '王秀兰', created_at: '2024-01-14 15:20:00',
        status: 'pending', status_display: '待审核',
        submission_data: { alias_name: '大柱子', usage_context: '家里长辈称呼' },
        has_conflict: false
      }
    ] : []
  }
  detailVisible.value = true
}

const claimTask = async (task) => {
  try {
    const res = await tasksApi.claim(task.id, { claimed_by: CURRENT_USER })
    ElMessage.success('任务认领成功！')
    task.status = 'in_progress'
    task.status_display = '处理中'
    task.claimed_by = CURRENT_USER
    task.claimed_at = new Date().toISOString()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '认领失败')
  }
}

const openSubmit = (task) => {
  currentTask.value = task
  submitData.value = {}
  submitFormText.value = ''
  loadPersons()
  submitVisible.value = true
}

const doSubmit = async () => {
  try {
    const res = await tasksApi.submit(currentTask.value.id, {
      submitter: CURRENT_USER,
      submission_data: submitData.value,
      submission_text: submitFormText.value
    })
    if (res.has_conflict) {
      ElMessage.warning('提交内容与既有信息存在冲突，已转入家庭确认台进行投票')
    } else {
      ElMessage.success('提交成功，等待审核')
    }
    currentTask.value.status = res.has_conflict ? 'conflicted' : 'submitted'
    currentTask.value.status_display = res.has_conflict ? '进入确认台' : '待审核'
    submitVisible.value = false
    detailVisible.value = false
    loadTasks()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '提交失败')
  }
}

const openReview = async (task) => {
  currentTask.value = task
  latestSubmission.value = null
  reviewComment.value = ''
  try {
    const res = await tasksApi.submissions(task.id)
    const list = res || []
    latestSubmission.value = list[list.length - 1]
  } catch (e) {
    latestSubmission.value = {
      id: 1, submitter: '王秀兰', created_at: '2024-01-14 15:20:00',
      status: 'pending', status_display: '待审核',
      submission_data: { alias_name: '大柱子', usage_context: '家里长辈称呼' },
      submission_text: '',
      has_conflict: false,
      conflict_description: ''
    }
  }
  reviewVisible.value = true
}

const doReview = async (action) => {
  try {
    await tasksApi.review(currentTask.value.id, {
      reviewer: CURRENT_USER,
      action,
      comment: reviewComment.value
    })
    const map = { approve: '已完成', reject: '已驳回', to_conflict: '进入确认台' }
    ElMessage.success(`审核完成：${map[action]}`)
    currentTask.value.status = action === 'approve' ? 'completed' : (action === 'reject' ? 'rejected' : 'conflicted')
    currentTask.value.status_display = map[action]
    reviewVisible.value = false
    detailVisible.value = false
    loadTasks()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '审核失败')
  }
}

const doGenerate = async () => {
  try {
    const res = await tasksApi.generate({
      source_type: genForm.value.source_type,
      task_types: genForm.value.task_types,
      assign_type: genForm.value.assign_type,
      assigned_to: genForm.value.assigned_to,
      created_by: CURRENT_USER
    })
    ElMessage.success(`成功生成 ${res.count || 0} 个任务`)
    showGenerate.value = false
    loadTasks()
    loadTaskStats()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || '生成失败，请手动创建')
  }
}

const openCreateTask = () => {
  ElMessageBox.prompt('请输入任务标题（简单版创建）', '新建采集任务', {
    confirmButtonText: '创建',
    cancelButtonText: '取消',
    inputPattern: /.+/,
    inputErrorMessage: '标题不能为空'
  }).then(async ({ value }) => {
    try {
      await tasksApi.create({
        task_type: 'event_narration',
        title: value,
        description: '手动创建的任务，请根据实际情况补充',
        source_type: 'photo',
        assign_type: 'family',
        created_by: CURRENT_USER
      })
      ElMessage.success('任务创建成功')
      loadTasks()
    } catch (e) {
      ElMessage.error('创建失败')
    }
  }).catch(() => {})
}

const onPageChange = (p) => {
  currentPage.value = p
  loadTasks()
}

const renderMyContribChart = () => {
  if (!myContribChart.value) return
  if (myChartInstance) myChartInstance.dispose()
  myChartInstance = echarts.init(myContribChart.value)
  const byType = myContribution.value?.by_type || []
  const data = byType.map(b => ({
    name: getContribLabel(b.contribution_type),
    value: b.count || 0,
    points: b.points || 0
  }))
  const option = {
    tooltip: { trigger: 'item', formatter: (p) => `${p.name}: ${p.value}次 / ${p.data.points || 0}分` },
    legend: { bottom: 0, textStyle: { color: '#5D4E3A' } },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '45%'],
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { color: '#5D4E3A', formatter: '{b}\n{d}%' },
      data: data.length ? data : [
        { name: '暂无数据', value: 1, itemStyle: { color: '#F5EDE0' }, label: { color: '#B5A48C' } }
      ]
    }]
  }
  myChartInstance.setOption(option)
}

const renderTypeChart = () => {
  if (!typeChart.value) return
  if (typeChartInstance) typeChartInstance.dispose()
  typeChartInstance = echarts.init(typeChart.value)
  const list = taskStats.value?.task_type_distribution || []
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 10, right: 20, top: 10, bottom: 30, containLabel: true },
    xAxis: { type: 'category', axisLabel: { show: false } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#F5EDE0' } } },
    series: [
      {
        name: '任务总数', type: 'bar', stack: 't',
        data: list.map(l => l.count - (l.completed || 0)),
        itemStyle: { color: '#F4A460', borderRadius: [0, 0, 0, 0] }
      },
      {
        name: '已完成', type: 'bar', stack: 't',
        data: list.map(l => l.completed || 0),
        itemStyle: { color: '#10B981', borderRadius: [6, 6, 0, 0] },
        label: {
          show: true, position: 'top',
          color: '#8B4513',
          formatter: (p) => list[p.dataIndex]?.count || ''
        }
      }
    ]
  }
  typeChartInstance.setOption(option)
}

watch(() => taskStats.value, () => {
  nextTick(() => {
    renderTypeChart()
    if (activeTab.value === 'mine') renderMyContribChart()
  })
}, { deep: true })

const handleResize = () => {
  myChartInstance?.resize()
  typeChartInstance?.resize()
}

onMounted(() => {
  const q = route.query
  if (q.source_type) filterSource.value = String(q.source_type)
  if (q.related_id) filterRelatedId.value = String(q.related_id)
  if (q.task_type) filterType.value = String(q.task_type)
  if (q.status) filterStatus.value = String(q.status)
  loadTasks()
  loadTaskStats()
  loadPersons()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.tasks-page {}
.page-header {
  margin-bottom: 20px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #8B4513;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.page-subtitle {
  color: #8B7355;
  font-size: 13px;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.ov-card {
  padding: 18px 20px;
  border-radius: 14px;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
.ov-card::after {
  content: '';
  position: absolute;
  top: -25px; right: -25px;
  width: 90px; height: 90px;
  background: rgba(255,255,255,0.15);
  border-radius: 50%;
}
.ov-blue { background: linear-gradient(135deg,#3B82F6,#60A5FA); }
.ov-orange { background: linear-gradient(135deg,#F59E0B,#FBBF24); }
.ov-purple { background: linear-gradient(135deg,#8B5CF6,#A78BFA); }
.ov-green { background: linear-gradient(135deg,#10B981,#34D399); }
.ov-red { background: linear-gradient(135deg,#EF4444,#F87171); }
.ov-icon { font-size: 30px; margin-bottom: 8px; position: relative; z-index: 1; }
.ov-num { font-size: 28px; font-weight: 700; line-height: 1; position: relative; z-index: 1; }
.ov-label { font-size: 13px; opacity: 0.95; margin: 6px 0 4px; position: relative; z-index: 1; }
.ov-desc { font-size: 11px; opacity: 0.75; position: relative; z-index: 1; }

.layout-row {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 20px;
}
.main-panel, .side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.panel-card {
  padding: 20px 24px;
  border-radius: 14px;
  background: #fff;
  border: 1px solid #F5EDE0;
  box-shadow: 0 2px 10px rgba(139,69,19,0.05);
}
.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #F5EDE0;
}
.header-actions { display: flex; gap: 8px; }

.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.task-list { display: flex; flex-direction: column; gap: 12px; }
.task-card {
  display: flex;
  padding: 16px 18px;
  background: linear-gradient(135deg,#FFFAF0,#FFF8F0);
  border: 1px solid #F5EDE0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.task-card:hover {
  box-shadow: 0 4px 14px rgba(139,69,19,0.1);
  transform: translateY(-1px);
}
.task-left { flex: 1; min-width: 0; }
.task-right { display: flex; align-items: center; margin-left: 12px; flex-shrink: 0; }
.task-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid;
  margin-bottom: 8px;
}
.task-type-badge.lg { padding: 4px 14px; font-size: 13px; }
.task-title {
  font-size: 15px;
  font-weight: 600;
  color: #5D4E3A;
  margin-bottom: 6px;
  line-height: 1.4;
}
.task-desc {
  font-size: 12px;
  color: #8B7355;
  margin-bottom: 10px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.task-meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  align-items: center;
  font-size: 12px;
  color: #8B7355;
}
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.highlight-assign { color: #F59E0B; font-weight: 600; }
.highlight-claim { color: #3B82F6; font-weight: 600; }
.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
.empty-state { padding: 40px 0; }

.my-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}
.my-stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: linear-gradient(135deg,#FFFAF0,#FFF8F0);
  border: 1px solid #F5EDE0;
  border-radius: 12px;
}
.my-stat-icon {
  width: 50px; height: 50px;
  border-radius: 14px;
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}
.my-stat-num { font-size: 24px; font-weight: 700; color: #5D4E3A; line-height: 1; }
.my-stat-label { font-size: 12px; color: #8B7355; margin-top: 4px; }

.section-block { margin-bottom: 24px; }
.section-block:last-child { margin-bottom: 0; }
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E3A;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 3px solid #D2691E;
}
.chart-area { width: 100%; height: 240px; }

.contrib-timeline { padding: 4px 0; }
.timeline-item {
  position: relative;
  display: flex;
  gap: 14px;
  padding-bottom: 16px;
  padding-left: 4px;
}
.timeline-item::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 22px;
  bottom: 0;
  width: 2px;
  background: #F5EDE0;
}
.timeline-item:last-child::before { display: none; }
.timeline-dot {
  width: 16px; height: 16px;
  border-radius: 50%;
  background: #D2691E;
  flex-shrink: 0;
  margin-top: 3px;
  box-shadow: 0 0 0 4px #FEF3E2;
  z-index: 1;
}
.timeline-content { flex: 1; }
.timeline-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.timeline-type { font-weight: 600; color: #5D4E3A; font-size: 13px; }
.timeline-time { font-size: 11px; color: #B5A48C; }
.timeline-desc { font-size: 12px; color: #8B7355; margin-bottom: 4px; }
.timeline-points { font-size: 12px; color: #10B981; font-weight: 600; }
.empty-timeline { padding: 20px; text-align: center; color: #B5A48C; font-size: 13px; }

.ranking-list { display: flex; flex-direction: column; gap: 10px; }
.rank-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: linear-gradient(135deg,#FFFAF0,#FFF8F0);
  border: 1px solid #F5EDE0;
  border-radius: 12px;
  transition: all 0.2s;
}
.rank-item:hover { box-shadow: 0 4px 12px rgba(139,69,19,0.08); }
.rank-item.rank-me { border-color: #F59E0B; background: linear-gradient(135deg,#FEF3C7,#FDE68A); }
.rank-pos {
  width: 36px; height: 36px;
  border-radius: 10px;
  background: #F5EDE0;
  color: #8B7355;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
}
.rank-1 { background: linear-gradient(135deg,#FEF3C7,#FDE68A); color: #92400E; }
.rank-2 { background: linear-gradient(135deg,#F3F4F6,#E5E7EB); color: #374151; }
.rank-3 { background: linear-gradient(135deg,#FFEDD5,#FED7AA); color: #92400E; }
.rank-avatar {
  width: 40px; height: 40px;
  border-radius: 50%;
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}
.rank-info { flex: 1; min-width: 0; }
.rank-name {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E3A;
  display: flex; align-items: center; gap: 6px;
  margin-bottom: 4px;
}
.rank-stats { display: flex; gap: 12px; font-size: 11px; color: #8B7355; }
.rank-points { text-align: right; flex-shrink: 0; }
.points-num { font-size: 22px; font-weight: 700; color: #8B4513; line-height: 1; }
.points-label { font-size: 11px; color: #8B7355; margin-top: 2px; }

.side-title {
  font-size: 15px;
  font-weight: 600;
  color: #5D4E3A;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 3px solid #F4A460;
}
.side-list { display: flex; flex-direction: column; gap: 10px; }
.side-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: #FFFAF0;
  border-radius: 8px;
}
.side-rank {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: #F4A460;
  color: white;
  font-size: 11px;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.side-info { flex: 1; min-width: 0; }
.side-name { font-size: 12px; color: #5D4E3A; font-weight: 600; margin-bottom: 4px; }
.side-count {
  font-size: 12px;
  color: #8B4513;
  font-weight: 700;
  flex-shrink: 0;
}

.task-detail {}
.detail-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.detail-title {
  font-size: 20px;
  font-weight: 700;
  color: #5D4E3A;
  margin-bottom: 8px;
}
.detail-desc {
  color: #8B7355;
  font-size: 13px;
  margin-bottom: 18px;
  line-height: 1.6;
}
.detail-section {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid #F5EDE0;
}
.detail-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E3A;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.submission-list { display: flex; flex-direction: column; gap: 14px; }
.sub-item {
  padding: 14px;
  background: #FFFAF0;
  border: 1px solid #F5EDE0;
  border-radius: 10px;
}
.sub-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.sub-meta { flex: 1; min-width: 0; }
.sub-user { font-size: 13px; font-weight: 600; color: #5D4E3A; }
.sub-time { font-size: 11px; color: #B5A48C; margin-top: 2px; }
.sub-text {
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  color: #5D4E3A;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 8px;
}
.sub-data { margin-bottom: 8px; }
.data-row {
  display: flex;
  gap: 8px;
  padding: 5px 0;
  font-size: 13px;
}
.data-key { color: #8B7355; min-width: 90px; }
.data-val { color: #5D4E3A; font-weight: 500; }
.sub-conflict {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: #FEF2F2;
  color: #DC2626;
  border-radius: 6px;
  font-size: 12px;
  margin-bottom: 8px;
}
.sub-review {
  padding: 10px 12px;
  background: #EFF6FF;
  border-radius: 8px;
  border-left: 3px solid #3B82F6;
}
.review-label { font-size: 12px; color: #3B82F6; font-weight: 600; margin-bottom: 4px; }
.review-text { font-size: 12px; color: #1E40AF; line-height: 1.5; }

.submit-form, .review-form, .gen-form {}
.form-hint { margin-bottom: 16px; }

.review-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid #F5EDE0;
}
.review-user { display: flex; align-items: center; gap: 12px; }
.review-name { font-size: 15px; font-weight: 600; color: #5D4E3A; }
.review-time { font-size: 12px; color: #B5A48C; margin-top: 2px; }
.review-content { margin-bottom: 16px; }
.review-block {
  margin-bottom: 12px;
  font-size: 13px;
}
.review-block label {
  display: block;
  color: #8B7355;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
}
.review-text-block {
  padding: 10px 12px;
  background: #FFFAF0;
  border-radius: 8px;
  color: #5D4E3A;
  line-height: 1.6;
}
.data-table {
  padding: 10px 12px;
  background: #FFFAF0;
  border-radius: 8px;
}
.review-block.conflict {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px;
  background: #FEF2F2;
  color: #DC2626;
  border-radius: 8px;
  margin-top: 14px;
}

.dialog-footer { display: flex; justify-content: flex-end; gap: 8px; }
</style>