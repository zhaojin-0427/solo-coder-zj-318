<template>
  <div class="artifacts-page">
    <div class="page-header">
      <div class="page-title">
        <el-icon><Box /></el-icon>
        物件记忆馆
      </div>
      <div class="page-subtitle">珍藏家族老物件、家书、票证、奖状、证件、手稿等非照片类素材，传承家族历史与记忆</div>
    </div>

    <div class="card-warm" style="padding: 20px; margin-bottom: 20px;">
      <div class="filter-row">
        <el-input v-model="searchText" placeholder="搜索物件名称、描述、地点、故事..." style="width: 280px;" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterType" placeholder="按类型" clearable style="width: 140px">
          <el-option v-for="t in TYPE_OPTIONS" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
        <el-select v-model="filterEra" placeholder="按年代" clearable style="width: 140px">
          <el-option v-for="e in ERA_OPTIONS" :key="e.value" :label="e.label" :value="e.value" />
        </el-select>
        <el-input v-model="filterCustodian" placeholder="保管人" clearable style="width: 140px">
          <template #prefix><el-icon><User /></el-icon></template>
        </el-input>
        <el-input v-model="filterLocation" placeholder="地点" clearable style="width: 140px">
          <template #prefix><el-icon><Location /></el-icon></template>
        </el-input>
        <el-select v-model="filterStatus" placeholder="确认状态" clearable style="width: 140px">
          <el-option v-for="s in STATUS_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-button type="primary" class="btn-primary-warm" @click="showCreate = true">
          <el-icon><Plus /></el-icon>新建物件
        </el-button>
      </div>
    </div>

    <div class="stat-summary-row" v-if="artifactStats">
      <div class="stat-mini">
        <span class="stat-num">{{ artifactStats.total_artifacts || 0 }}</span>
        <span class="stat-label">物件总数</span>
      </div>
      <div class="stat-mini">
        <span class="stat-num warn">{{ artifactStats.pending_artifacts || 0 }}</span>
        <span class="stat-label">待确认</span>
      </div>
      <div class="stat-mini">
        <span class="stat-num danger">{{ artifactStats.conflicted_artifacts || 0 }}</span>
        <span class="stat-label">有争议</span>
      </div>
      <div class="stat-mini">
        <span class="stat-num success">{{ artifactStats.story_completed_count || 0 }}</span>
        <span class="stat-label">有故事</span>
      </div>
      <div class="stat-mini">
        <span class="stat-num">{{ artifactStats.story_completion_rate || 0 }}%</span>
        <span class="stat-label">故事完成度</span>
      </div>
    </div>

    <div v-if="loading" class="card-warm" style="padding: 40px; text-align: center;">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <div style="margin-top: 12px; color: #8B7355;">加载中...</div>
    </div>

    <div v-else-if="!filteredArtifacts.length" class="card-warm empty-warm">
      <el-icon :size="48" style="color: #D4A574; margin-bottom: 12px;"><Box /></el-icon>
      <div>还没有录入物件</div>
      <div style="font-size: 13px; margin-top: 8px;">点击"新建物件"按钮开始家族物件记忆的整理之旅</div>
    </div>

    <div v-else class="artifact-grid">
      <div
        v-for="artifact in filteredArtifacts"
        :key="artifact.id"
        class="artifact-card"
        @click="openDetail(artifact)"
      >
        <div class="artifact-thumb">
          <img :src="artifact.image_url" v-if="artifact.image_url" />
          <span class="artifact-emoji" v-else>{{ getTypeEmoji(artifact.artifact_type) }}</span>
          <el-tag v-if="artifact.has_dispute" size="small" class="dispute-badge">
            <el-icon><Warning /></el-icon>有争议
          </el-tag>
        </div>
        <div class="artifact-info">
          <div class="artifact-title">{{ artifact.name || '未命名物件' }}</div>
          <div class="artifact-meta">
            <el-tag size="small" class="tag-type">{{ getOptionLabel(TYPE_OPTIONS, artifact.artifact_type) }}</el-tag>
            <el-tag size="small" class="tag-era">{{ getOptionLabel(ERA_OPTIONS, artifact.era) }}</el-tag>
          </div>
          <div class="artifact-desc" v-if="artifact.description">{{ artifact.description }}</div>
          <div class="artifact-footer">
            <span class="artifact-custodian" v-if="artifact.current_custodian">
              <el-icon><User /></el-icon>
              {{ artifact.current_custodian }}
            </span>
            <span class="artifact-location" v-if="artifact.location">
              <el-icon><Location /></el-icon>
              {{ artifact.location }}
            </span>
          </div>
          <div class="artifact-stats">
            <span><el-icon><UserFilled /></el-icon>{{ artifact.person_count || 0 }}</span>
            <span><el-icon><Picture /></el-icon>{{ artifact.photo_count || 0 }}</span>
            <span><el-icon><Document /></el-icon>{{ artifact.memory_count || 0 }}</span>
            <el-tag size="small" :type="getStatusType(artifact.status)" effect="light">
              {{ getOptionLabel(STATUS_OPTIONS, artifact.status) }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showCreate" :title="editingArtifact ? '编辑物件' : '新建物件'" width="680px" destroy-on-close>
      <el-form :model="artifactForm" label-width="100px">
        <el-form-item label="物件名称">
          <el-input v-model="artifactForm.name" placeholder="如：祖父的怀表" />
        </el-form-item>
        <el-form-item label="物件类型">
          <el-select v-model="artifactForm.artifact_type" style="width: 100%">
            <el-option v-for="t in TYPE_OPTIONS" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="物件照片">
          <el-upload
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleImageChange"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖放照片到此处或<em>点击选择</em></div>
            <template #tip>
              <div class="el-upload__tip">支持 JPG/PNG 格式</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="年代">
          <el-select v-model="artifactForm.era" style="width: 100%">
            <el-option v-for="e in ERA_OPTIONS" :key="e.value" :label="e.label" :value="e.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="具体年份">
          <el-input-number v-model="artifactForm.year" :min="1800" :max="2030" placeholder="选填" />
          <el-checkbox v-model="artifactForm.year_unknown" style="margin-left: 16px;">年份未知</el-checkbox>
        </el-form-item>
        <el-form-item label="出土地/来源地">
          <el-input v-model="artifactForm.location" placeholder="如：浙江绍兴老家" />
        </el-form-item>
        <el-form-item label="材质">
          <el-select v-model="artifactForm.material" style="width: 100%">
            <el-option v-for="m in MATERIAL_OPTIONS" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="保存状况">
          <el-select v-model="artifactForm.condition" style="width: 100%">
            <el-option v-for="c in CONDITION_OPTIONS" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="尺寸">
          <el-input v-model="artifactForm.size" placeholder="如：长20cm宽15cm高5cm" />
        </el-form-item>
        <el-form-item label="当前保管人">
          <el-input v-model="artifactForm.current_custodian" placeholder="如：大伯" />
        </el-form-item>
        <el-form-item label="保管人关系">
          <el-input v-model="artifactForm.custodian_relation" placeholder="如：长子" />
        </el-form-item>
        <el-form-item label="获取方式">
          <el-input v-model="artifactForm.acquisition_method" placeholder="如：祖传、购买、赠送等" />
        </el-form-item>
        <el-form-item label="物件描述">
          <el-input
            v-model="artifactForm.description"
            type="textarea"
            :rows="3"
            placeholder="外观、特征、印记等详细描述"
          />
        </el-form-item>
        <el-form-item label="背后故事">
          <el-input
            v-model="artifactForm.story"
            type="textarea"
            :rows="4"
            placeholder="物件的来历、意义、相关故事等"
          />
        </el-form-item>
        <el-form-item label="建档人">
          <el-input v-model="artifactForm.created_by" placeholder="家属" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitArtifact">保存归档</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetail" :title="currentArtifact?.name || '物件详情'" width="860px" destroy-on-close>
      <div v-if="currentArtifact" class="artifact-detail">
        <div class="detail-header">
          <div class="detail-image">
            <img :src="currentArtifact.image_url" v-if="currentArtifact.image_url" />
            <div class="no-image" v-else>
              <el-icon :size="64"><Box /></el-icon>
              <span>暂无照片</span>
            </div>
          </div>
          <div class="detail-basic">
            <h2>{{ currentArtifact.name }}</h2>
            <div class="detail-tags">
              <el-tag type="primary">{{ getOptionLabel(TYPE_OPTIONS, currentArtifact.artifact_type) }}</el-tag>
              <el-tag>{{ getOptionLabel(ERA_OPTIONS, currentArtifact.era) }}</el-tag>
              <el-tag v-if="currentArtifact.year">{{ currentArtifact.year }}年</el-tag>
              <el-tag :type="getStatusType(currentArtifact.status)" effect="light">
                {{ getOptionLabel(STATUS_OPTIONS, currentArtifact.status) }}
              </el-tag>
            </div>
            <div class="detail-info-grid">
              <div class="info-item">
                <span class="info-label">材质</span>
                <span class="info-value">{{ getOptionLabel(MATERIAL_OPTIONS, currentArtifact.material) || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">保存状况</span>
                <span class="info-value">{{ getOptionLabel(CONDITION_OPTIONS, currentArtifact.condition) || '未知' }}</span>
              </div>
              <div class="info-item" v-if="currentArtifact.size">
                <span class="info-label">尺寸</span>
                <span class="info-value">{{ currentArtifact.size }}</span>
              </div>
              <div class="info-item" v-if="currentArtifact.weight">
                <span class="info-label">重量</span>
                <span class="info-value">{{ currentArtifact.weight }}</span>
              </div>
              <div class="info-item" v-if="currentArtifact.current_custodian">
                <span class="info-label">当前保管人</span>
                <span class="info-value">{{ currentArtifact.current_custodian }} ({{ currentArtifact.custodian_relation || '家属' }})</span>
              </div>
              <div class="info-item" v-if="currentArtifact.location">
                <span class="info-label">来源地</span>
                <span class="info-value">{{ currentArtifact.location }}</span>
              </div>
              <div class="info-item" v-if="currentArtifact.acquisition_method">
                <span class="info-label">获取方式</span>
                <span class="info-value">{{ currentArtifact.acquisition_method }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">建档人</span>
                <span class="info-value">{{ currentArtifact.created_by || '家属' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-actions">
          <el-button @click="editArtifact">
            <el-icon><Edit /></el-icon>编辑
          </el-button>
          <el-button type="primary" @click="showAddStory = true">
            <el-icon><DocumentAdd /></el-icon>补充故事
          </el-button>
          <el-button type="warning" @click="showSubmitDispute = true">
            <el-icon><Warning /></el-icon>提交争议
          </el-button>
          <el-button type="success" @click="showCreateTask = true">
            <el-icon><List /></el-icon>发起采集任务
          </el-button>
          <el-button type="primary" plain @click="confirmArchive" v-if="currentArtifact.status === 'pending'">
            <el-icon><CircleCheck /></el-icon>确认归档
          </el-button>
          <el-dropdown @command="handleLinkCommand" style="margin-left: auto;">
            <el-button>
              <el-icon><Link /></el-icon>关联...
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="person">关联人物</el-dropdown-item>
                <el-dropdown-item command="photo">关联照片</el-dropdown-item>
                <el-dropdown-item command="memory">关联回忆</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="物件描述" name="description">
            <div class="tab-content">
              <p v-if="currentArtifact.description">{{ currentArtifact.description }}</p>
              <p v-else style="color: #999;">暂无描述</p>
            </div>
          </el-tab-pane>

          <el-tab-pane label="背后故事" name="story">
            <div class="tab-content">
              <div v-if="currentArtifact.story" class="story-main">
                <h4>主要故事</h4>
                <p>{{ currentArtifact.story }}</p>
              </div>
              <div v-if="storySupplements.length">
                <h4>更多补注故事</h4>
                <div v-for="s in storySupplements" :key="s.id" class="story-item">
                  <div class="story-header">
                    <span class="story-title">{{ s.title || '故事补注' }}</span>
                    <span class="story-meta">{{ s.added_by }} · {{ formatDate(s.created_at) }}</span>
                  </div>
                  <p>{{ s.content }}</p>
                </div>
              </div>
              <div v-if="!currentArtifact.story && !storySupplements.length" style="color: #999;">
                暂无故事，点击"补充故事"添加物件背后的故事
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="关联人物" name="persons">
            <div class="tab-content">
              <div v-if="relatedPersons.length" class="related-list">
                <div v-for="r in relatedPersons" :key="r.id" class="related-item">
                  <el-avatar :size="40">{{ r.person_detail?.name?.charAt(0) || '?' }}</el-avatar>
                  <div class="related-info">
                    <div class="related-name">{{ r.person_detail?.name || '未知人物' }}</div>
                    <div class="related-note">{{ r.relation_type_display }} {{ r.relation_note ? '· ' + r.relation_note : '' }}</div>
                  </div>
                  <el-button size="small" text type="danger" @click="unlinkItem('person', r.id)">
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
              </div>
              <div v-else style="color: #999;">暂无关联人物</div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="关联照片" name="photos">
            <div class="tab-content">
              <div v-if="relatedPhotos.length" class="related-photos-grid">
                <div v-for="r in relatedPhotos" :key="r.id" class="related-photo-item">
                  <img :src="r.photo_detail?.image_url" v-if="r.photo_detail?.image_url" />
                  <div class="no-photo" v-else>
                    <el-icon><Picture /></el-icon>
                  </div>
                  <div class="photo-caption">{{ r.photo_detail?.title || '未命名照片' }}</div>
                  <el-button size="small" text type="danger" @click="unlinkItem('photo', r.id)">
                    移除关联
                  </el-button>
                </div>
              </div>
              <div v-else style="color: #999;">暂无关联照片</div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="关联回忆" name="memories">
            <div class="tab-content">
              <div v-if="relatedMemories.length" class="related-list">
                <div v-for="r in relatedMemories" :key="r.id" class="related-item">
                  <el-avatar :size="40" style="background: #D2691E;">
                    <el-icon><Document /></el-icon>
                  </el-avatar>
                  <div class="related-info">
                    <div class="related-name">{{ r.memory_title || '未命名回忆' }}</div>
                    <div class="related-note">{{ r.relation_note || '关联回忆' }}</div>
                  </div>
                  <el-button size="small" text type="danger" @click="unlinkItem('memory', r.id)">
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
              </div>
              <div v-else style="color: #999;">暂无关联回忆</div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="争议记录" name="disputes">
            <div class="tab-content">
              <div v-if="disputes.length">
                <div v-for="d in disputes" :key="d.id" class="dispute-item">
                  <div class="dispute-header">
                    <el-tag :type="d.status === 'open' ? 'warning' : d.status === 'resolved' ? 'success' : 'info'">
                      {{ d.status_display }}
                    </el-tag>
                    <span class="dispute-field">{{ d.dispute_field_display }}</span>
                    <span class="dispute-date">{{ formatDate(d.created_at) }}</span>
                  </div>
                  <div class="dispute-versions">
                    <div class="version-card original">
                      <div class="version-label">原版本</div>
                      <div class="version-author">{{ d.version_original_author || '原数据' }}</div>
                      <div class="version-content">{{ d.version_original || '空' }}</div>
                    </div>
                    <div class="version-vs">VS</div>
                    <div class="version-card new">
                      <div class="version-label">争议版本</div>
                      <div class="version-author">{{ d.version_new_author }}</div>
                      <div class="version-content">{{ d.version_new }}</div>
                    </div>
                  </div>
                  <div class="dispute-actions" v-if="d.status === 'open'">
                    <el-button size="small" type="success" @click="resolveDispute(d.id, 'new')">采纳新版本</el-button>
                    <el-button size="small" type="info" @click="resolveDispute(d.id, 'original')">保留原版本</el-button>
                    <el-button size="small" type="warning" @click="resolveDispute(d.id, 'merged')">合并版本</el-button>
                  </div>
                </div>
              </div>
              <div v-else style="color: #999;">暂无争议记录</div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <el-dialog v-model="showAddStory" title="补充物件故事" width="520px" destroy-on-close>
      <el-form :model="storyForm" label-width="100px">
        <el-form-item label="故事标题">
          <el-input v-model="storyForm.title" placeholder="选填，如：爷爷的怀表故事" />
        </el-form-item>
        <el-form-item label="补注视角">
          <el-input v-model="storyForm.perspective" placeholder="如：使用经历、获得过程等" />
        </el-form-item>
        <el-form-item label="故事内容">
          <el-input v-model="storyForm.content" type="textarea" :rows="5" placeholder="请详细描述物件背后的故事..." />
        </el-form-item>
        <el-form-item label="补注人">
          <el-input v-model="storyForm.added_by" placeholder="家属" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="storyForm.is_primary">设为主要故事</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddStory = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitStory">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showSubmitDispute" title="提交信息争议" width="520px" destroy-on-close>
      <el-form :model="disputeForm" label-width="100px">
        <el-form-item label="争议字段">
          <el-select v-model="disputeForm.dispute_field" style="width: 100%">
            <el-option v-for="f in DISPUTE_FIELD_OPTIONS" :key="f.value" :label="f.label" :value="f.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="您的版本">
          <el-input v-model="disputeForm.version_new" type="textarea" :rows="4" placeholder="请输入您认为正确的信息..." />
        </el-form-item>
        <el-form-item label="提交人">
          <el-input v-model="disputeForm.version_new_author" placeholder="家属" />
        </el-form-item>
        <el-form-item label="争议说明">
          <el-input v-model="disputeForm.description" type="textarea" :rows="3" placeholder="请说明争议原因..." />
        </el-form-item>
        <el-form-item label="证据说明">
          <el-input v-model="disputeForm.evidence" type="textarea" :rows="2" placeholder="可提供证据或参考来源..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSubmitDispute = false">取消</el-button>
        <el-button type="warning" @click="submitDispute">提交争议</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showLinkPerson" title="关联人物" width="520px" destroy-on-close>
      <el-select
        v-model="linkPersonId"
        filterable
        placeholder="搜索并选择人物"
        style="width: 100%;"
      >
        <el-option
          v-for="p in personOptions"
          :key="p.id"
          :label="p.name"
          :value="p.id"
        />
      </el-select>
      <el-input
        v-model="linkRelationType"
        placeholder="关系类型，如：所有者、使用者、制作者等"
        style="margin-top: 12px;"
      />
      <el-input
        v-model="linkRelationNote"
        placeholder="关系说明（选填）"
        style="margin-top: 12px;"
      />
      <template #footer>
        <el-button @click="showLinkPerson = false">取消</el-button>
        <el-button type="primary" @click="confirmLinkPerson">确认关联</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCreateTask" title="发起采集任务" width="520px" destroy-on-close>
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务类型">
          <el-select v-model="taskForm.task_type" style="width: 100%">
            <el-option label="物件鉴定/识别" value="artifact_identify" />
            <el-option label="物件故事补注" value="artifact_story" />
            <el-option label="物件来源考证" value="artifact_source" />
            <el-option label="物件年代确认" value="artifact_era" />
            <el-option label="物件保管人确认" value="artifact_custodian" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" placeholder="选填，自动生成" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" placeholder="选填" />
        </el-form-item>
        <el-form-item label="分派方式">
          <el-radio-group v-model="taskForm.assign_type">
            <el-radio value="family">全家开放</el-radio>
            <el-radio value="specific">指定人员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="指定人员" v-if="taskForm.assign_type === 'specific'">
          <el-input v-model="taskForm.assigned_to" placeholder="请输入家属姓名" />
        </el-form-item>
        <el-form-item label="创建人">
          <el-input v-model="taskForm.created_by" placeholder="家属" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateTask = false">取消</el-button>
        <el-button type="primary" @click="submitCreateTask">创建任务</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Box, Search, User, Location, Plus, Picture, Document,
  UploadFilled, Loading, Warning, Edit, DocumentAdd,
  List, CircleCheck, Link, ArrowDown, Close, UserFilled
} from '@element-plus/icons-vue'
import { artifacts, persons, photos, memories } from '@/api'

const TYPE_OPTIONS = [
  { value: 'old_object', label: '老物件' },
  { value: 'letter', label: '家书' },
  { value: 'ticket', label: '票证' },
  { value: 'certificate', label: '奖状' },
  { value: 'document', label: '证件' },
  { value: 'manuscript', label: '手稿' },
  { value: 'book', label: '书籍' },
  { value: 'clothing', label: '服饰' },
  { value: 'jewelry', label: '首饰' },
  { value: 'furniture', label: '家具' },
  { value: 'tool', label: '工具' },
  { value: 'other', label: '其他' }
]

const ERA_OPTIONS = [
  { value: 'qing_dynasty', label: '清代' },
  { value: 'republic', label: '民国' },
  { value: '1900s', label: '1900年代' },
  { value: '1910s', label: '1910年代' },
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

const STATUS_OPTIONS = [
  { value: 'pending', label: '待确认' },
  { value: 'confirmed', label: '已确认' },
  { value: 'conflicted', label: '有争议' },
  { value: 'archived', label: '已归档' }
]

const MATERIAL_OPTIONS = [
  { value: 'paper', label: '纸质' },
  { value: 'fabric', label: '织物' },
  { value: 'metal', label: '金属' },
  { value: 'wood', label: '木质' },
  { value: 'ceramic', label: '陶瓷' },
  { value: 'glass', label: '玻璃' },
  { value: 'stone', label: '石质' },
  { value: 'plastic', label: '塑料' },
  { value: 'mixed', label: '混合材质' },
  { value: 'other', label: '其他' }
]

const CONDITION_OPTIONS = [
  { value: 'excellent', label: '完好' },
  { value: 'good', label: '较好' },
  { value: 'fair', label: '一般' },
  { value: 'poor', label: '较差' },
  { value: 'damaged', label: '破损' },
  { value: 'repaired', label: '已修复' }
]

const DISPUTE_FIELD_OPTIONS = [
  { value: 'name', label: '物件名称' },
  { value: 'type', label: '物件类型' },
  { value: 'era', label: '年代' },
  { value: 'year', label: '具体年份' },
  { value: 'location', label: '地点' },
  { value: 'source', label: '来源' },
  { value: 'custodian', label: '保管人' },
  { value: 'story', label: '背后故事' },
  { value: 'description', label: '物件描述' },
  { value: 'authenticity', label: '真伪' },
  { value: 'ownership', label: '归属权' },
  { value: 'other', label: '其他' }
]

const artifacts_list = ref([])
const artifactStats = ref(null)
const loading = ref(false)
const searchText = ref('')
const filterType = ref('')
const filterEra = ref('')
const filterCustodian = ref('')
const filterLocation = ref('')
const filterStatus = ref('')

const showCreate = ref(false)
const editingArtifact = ref(null)
const artifactForm = ref({
  name: '',
  artifact_type: 'old_object',
  era: 'unknown',
  year: null,
  year_unknown: false,
  location: '',
  material: '',
  condition: 'good',
  size: '',
  current_custodian: '',
  custodian_relation: '',
  acquisition_method: '',
  description: '',
  story: '',
  created_by: '家属'
})
const uploadImageFile = ref(null)

const showDetail = ref(false)
const currentArtifact = ref(null)
const activeTab = ref('description')
const relatedPersons = ref([])
const relatedPhotos = ref([])
const relatedMemories = ref([])
const disputes = ref([])
const storySupplements = ref([])

const showAddStory = ref(false)
const storyForm = ref({
  title: '',
  perspective: '',
  content: '',
  added_by: '家属',
  is_primary: false
})

const showSubmitDispute = ref(false)
const disputeForm = ref({
  dispute_field: 'story',
  version_new: '',
  version_new_author: '家属',
  description: '',
  evidence: ''
})

const showLinkPerson = ref(false)
const linkPersonId = ref(null)
const linkRelationType = ref('related')
const linkRelationNote = ref('')
const personOptions = ref([])

const showCreateTask = ref(false)
const taskForm = ref({
  task_type: 'artifact_story',
  title: '',
  description: '',
  assign_type: 'family',
  assigned_to: '',
  created_by: '家属'
})

const filteredArtifacts = computed(() => {
  let list = [...artifacts_list.value]
  if (searchText.value) {
    const kw = searchText.value.toLowerCase()
    list = list.filter(a =>
      (a.name || '').toLowerCase().includes(kw) ||
      (a.description || '').toLowerCase().includes(kw) ||
      (a.location || '').toLowerCase().includes(kw) ||
      (a.current_custodian || '').toLowerCase().includes(kw) ||
      (a.story || '').toLowerCase().includes(kw)
    )
  }
  if (filterType.value) {
    list = list.filter(a => a.artifact_type === filterType.value)
  }
  if (filterEra.value) {
    list = list.filter(a => a.era === filterEra.value)
  }
  if (filterCustodian.value) {
    const kw = filterCustodian.value.toLowerCase()
    list = list.filter(a => (a.current_custodian || '').toLowerCase().includes(kw))
  }
  if (filterLocation.value) {
    const kw = filterLocation.value.toLowerCase()
    list = list.filter(a => (a.location || '').toLowerCase().includes(kw))
  }
  if (filterStatus.value) {
    list = list.filter(a => a.status === filterStatus.value)
  }
  return list
})

const loadArtifacts = async () => {
  loading.value = true
  try {
    const data = await artifacts.list({ limit: 200 })
    if (data.results) {
      artifacts_list.value = data.results
    } else if (Array.isArray(data)) {
      artifacts_list.value = data
    } else {
      artifacts_list.value = []
    }
  } catch (e) {
    console.error('加载物件失败:', e)
    artifacts_list.value = []
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const data = await artifacts.stats()
    artifactStats.value = data
  } catch (e) {
    console.error('加载统计失败:', e)
  }
}

const loadPersonOptions = async () => {
  try {
    const data = await persons.simple()
    personOptions.value = data.results || data || []
  } catch (e) {
    console.error('加载人物列表失败:', e)
  }
}

const getTypeEmoji = (type) => {
  const emojiMap = {
    old_object: '📦',
    letter: '✉️',
    ticket: '🎫',
    certificate: '🏆',
    document: '📜',
    manuscript: '📝',
    book: '📚',
    clothing: '👔',
    jewelry: '💎',
    furniture: '🪑',
    tool: '🔧',
    other: '🎁'
  }
  return emojiMap[type] || '📦'
}

const getOptionLabel = (options, value) => {
  const opt = options.find(o => o.value === value)
  return opt ? opt.label : value
}

const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    confirmed: 'success',
    conflicted: 'danger',
    archived: 'info'
  }
  return map[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN')
}

const handleImageChange = (file) => {
  uploadImageFile.value = file.raw
}

const openDetail = async (artifact) => {
  currentArtifact.value = artifact
  activeTab.value = 'description'
  showDetail.value = true
  try {
    const detail = await artifacts.get(artifact.id)
    currentArtifact.value = detail
    loadRelatedData(artifact.id)
  } catch (e) {
    console.error('加载详情失败:', e)
  }
}

const loadRelatedData = async (artifactId) => {
  try {
    const [persons, photos, memories, dispList, stories] = await Promise.all([
      artifacts.relatedPersons(artifactId),
      artifacts.relatedPhotos(artifactId),
      artifacts.relatedMemories(artifactId),
      artifacts.disputesList(artifactId),
      artifacts.storySupplements(artifactId)
    ])
    relatedPersons.value = persons || []
    relatedPhotos.value = photos || []
    relatedMemories.value = memories || []
    disputes.value = dispList || []
    storySupplements.value = stories || []
  } catch (e) {
    console.error('加载关联数据失败:', e)
  }
}

const editArtifact = () => {
  if (!currentArtifact.value) return
  editingArtifact.value = currentArtifact.value
  artifactForm.value = {
    name: currentArtifact.value.name || '',
    artifact_type: currentArtifact.value.artifact_type || 'old_object',
    era: currentArtifact.value.era || 'unknown',
    year: currentArtifact.value.year || null,
    year_unknown: currentArtifact.value.year_unknown || false,
    location: currentArtifact.value.location || '',
    material: currentArtifact.value.material || '',
    condition: currentArtifact.value.condition || 'good',
    size: currentArtifact.value.size || '',
    current_custodian: currentArtifact.value.current_custodian || '',
    custodian_relation: currentArtifact.value.custodian_relation || '',
    acquisition_method: currentArtifact.value.acquisition_method || '',
    description: currentArtifact.value.description || '',
    story: currentArtifact.value.story || '',
    created_by: currentArtifact.value.created_by || '家属'
  }
  showDetail.value = false
  showCreate.value = true
}

const submitArtifact = async () => {
  if (!artifactForm.value.name) {
    ElMessage.warning('请输入物件名称')
    return
  }

  try {
    const formData = new FormData()
    Object.keys(artifactForm.value).forEach(key => {
      if (artifactForm.value[key] !== '' && artifactForm.value[key] !== null) {
        formData.append(key, artifactForm.value[key])
      }
    })
    if (uploadImageFile.value) {
      formData.append('image', uploadImageFile.value)
    }

    let result
    if (editingArtifact.value) {
      result = await artifacts.update(editingArtifact.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      result = await artifacts.create(formData)
      ElMessage.success('创建成功')
    }

    showCreate.value = false
    resetForm()
    loadArtifacts()
    loadStats()

    if (result && result.id) {
      currentArtifact.value = result
      showDetail.value = true
      loadRelatedData(result.id)
    }
  } catch (e) {
    console.error('保存失败:', e)
    ElMessage.error('保存失败，请重试')
  }
}

const resetForm = () => {
  artifactForm.value = {
    name: '',
    artifact_type: 'old_object',
    era: 'unknown',
    year: null,
    year_unknown: false,
    location: '',
    material: '',
    condition: 'good',
    size: '',
    current_custodian: '',
    custodian_relation: '',
    acquisition_method: '',
    description: '',
    story: '',
    created_by: '家属'
  }
  uploadImageFile.value = null
  editingArtifact.value = null
}

const submitStory = async () => {
  if (!storyForm.value.content) {
    ElMessage.warning('请输入故事内容')
    return
  }
  try {
    await artifacts.addStory(currentArtifact.value.id, storyForm.value)
    ElMessage.success('故事补注成功')
    showAddStory.value = false
    storyForm.value = {
      title: '',
      perspective: '',
      content: '',
      added_by: '家属',
      is_primary: false
    }
    loadRelatedData(currentArtifact.value.id)
    const detail = await artifacts.get(currentArtifact.value.id)
    currentArtifact.value = detail
  } catch (e) {
    console.error('提交故事失败:', e)
    ElMessage.error('提交失败')
  }
}

const submitDispute = async () => {
  if (!disputeForm.value.version_new) {
    ElMessage.warning('请输入您的版本')
    return
  }
  try {
    await artifacts.submitDispute(currentArtifact.value.id, disputeForm.value)
    ElMessage.success('争议已提交，将进入家庭确认流程')
    showSubmitDispute.value = false
    disputeForm.value = {
      dispute_field: 'story',
      version_new: '',
      version_new_author: '家属',
      description: '',
      evidence: ''
    }
    loadRelatedData(currentArtifact.value.id)
    const detail = await artifacts.get(currentArtifact.value.id)
    currentArtifact.value = detail
    loadStats()
  } catch (e) {
    console.error('提交争议失败:', e)
    ElMessage.error('提交失败')
  }
}

const resolveDispute = async (disputeId, version) => {
  try {
    await ElMessageBox.confirm('确认要这样处理吗？', '确认', { type: 'warning' })
    await artifacts.resolveDispute(currentArtifact.value.id, {
      dispute_id: disputeId,
      resolved_version: version,
      resolved_by: '家属'
    })
    ElMessage.success('处理成功')
    loadRelatedData(currentArtifact.value.id)
    const detail = await artifacts.get(currentArtifact.value.id)
    currentArtifact.value = detail
    loadStats()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('处理争议失败:', e)
      ElMessage.error('处理失败')
    }
  }
}

const handleLinkCommand = (cmd) => {
  if (cmd === 'person') {
    showLinkPerson.value = true
  } else if (cmd === 'photo') {
    ElMessage.info('照片关联功能开发中')
  } else if (cmd === 'memory') {
    ElMessage.info('回忆关联功能开发中')
  }
}

const confirmLinkPerson = async () => {
  if (!linkPersonId.value) {
    ElMessage.warning('请选择人物')
    return
  }
  try {
    await artifacts.link(currentArtifact.value.id, {
      target_type: 'person',
      target_id: linkPersonId.value,
      relation_type: linkRelationType.value,
      relation_note: linkRelationNote.value
    })
    ElMessage.success('关联成功')
    showLinkPerson.value = false
    linkPersonId.value = null
    linkRelationType.value = 'related'
    linkRelationNote.value = ''
    loadRelatedData(currentArtifact.value.id)
  } catch (e) {
    console.error('关联失败:', e)
    ElMessage.error('关联失败')
  }
}

const unlinkItem = async (type, relationId) => {
  try {
    await ElMessageBox.confirm('确认要移除关联吗？', '确认', { type: 'warning' })
    await artifacts.unlink(currentArtifact.value.id, {
      target_type: type,
      target_id: type === 'person' ? relatedPersons.value.find(r => r.id === relationId)?.person?.id :
                 type === 'photo' ? relatedPhotos.value.find(r => r.id === relationId)?.photo?.id :
                 relatedMemories.value.find(r => r.id === relationId)?.memory?.id
    })
    ElMessage.success('已移除关联')
    loadRelatedData(currentArtifact.value.id)
  } catch (e) {
    if (e !== 'cancel') {
      console.error('移除关联失败:', e)
    }
  }
}

const submitCreateTask = async () => {
  try {
    const result = await artifacts.createTask(currentArtifact.value.id, taskForm.value)
    ElMessage.success('任务创建成功')
    showCreateTask.value = false
    taskForm.value = {
      task_type: 'artifact_story',
      title: '',
      description: '',
      assign_type: 'family',
      assigned_to: '',
      created_by: '家属'
    }
  } catch (e) {
    console.error('创建任务失败:', e)
    ElMessage.error('创建失败')
  }
}

const confirmArchive = async () => {
  try {
    await ElMessageBox.confirm('确认归档此物件吗？', '确认归档', { type: 'success' })
    await artifacts.confirmArchive(currentArtifact.value.id, {
      confirmed_by: '家属',
      confirm_note: ''
    })
    ElMessage.success('已确认归档')
    const detail = await artifacts.get(currentArtifact.value.id)
    currentArtifact.value = detail
    loadArtifacts()
    loadStats()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('归档失败:', e)
      ElMessage.error('归档失败')
    }
  }
}

onMounted(() => {
  loadArtifacts()
  loadStats()
  loadPersonOptions()
})
</script>

<style scoped>
.artifacts-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #5D4037;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #8B7355;
  font-size: 14px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.stat-summary-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-mini {
  background: #FFF8F0;
  border: 1px solid #E8D5C4;
  border-radius: 8px;
  padding: 12px 20px;
  text-align: center;
  min-width: 100px;
}

.stat-mini .stat-num {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #5D4037;
}

.stat-mini .stat-num.warn {
  color: #E67E22;
}

.stat-mini .stat-num.danger {
  color: #C0392B;
}

.stat-mini .stat-num.success {
  color: #27AE60;
}

.stat-mini .stat-label {
  font-size: 12px;
  color: #8B7355;
}

.artifact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.artifact-card {
  background: #FFF8F0;
  border: 1px solid #E8D5C4;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.artifact-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(139, 115, 85, 0.15);
}

.artifact-thumb {
  position: relative;
  height: 160px;
  background: #F5E6D3;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.artifact-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.artifact-emoji {
  font-size: 64px;
}

.dispute-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #E74C3C !important;
  border-color: #C0392B !important;
}

.artifact-info {
  padding: 12px;
}

.artifact-title {
  font-size: 16px;
  font-weight: 600;
  color: #3E2723;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artifact-meta {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.tag-type {
  background: #D7CCC8 !important;
  color: #3E2723 !important;
  border: none !important;
}

.tag-era {
  background: #FFE0B2 !important;
  color: #E65100 !important;
  border: none !important;
}

.artifact-desc {
  font-size: 13px;
  color: #6D4C41;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.artifact-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #8B7355;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 6px;
}

.artifact-footer span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.artifact-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #8B7355;
  padding-top: 8px;
  border-top: 1px solid #E8D5C4;
}

.artifact-stats span {
  display: flex;
  align-items: center;
  gap: 3px;
}

.artifact-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.detail-image {
  width: 200px;
  height: 200px;
  background: #F5E6D3;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-image .no-image {
  text-align: center;
  color: #D4A574;
}

.detail-image .no-image span {
  display: block;
  margin-top: 8px;
  font-size: 13px;
}

.detail-basic {
  flex: 1;
}

.detail-basic h2 {
  margin: 0 0 12px 0;
  color: #3E2723;
  font-size: 22px;
}

.detail-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.detail-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #8B7355;
}

.info-value {
  font-size: 14px;
  color: #3E2723;
}

.detail-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 12px;
  background: #FFF8F0;
  border-radius: 8px;
}

.detail-tabs {
  margin-top: 20px;
}

.tab-content {
  padding: 12px 0;
}

.story-main {
  background: #FFF8F0;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.story-main h4 {
  margin: 0 0 8px 0;
  color: #5D4037;
}

.story-main p {
  margin: 0;
  color: #3E2723;
  line-height: 1.8;
}

.story-item {
  background: #FAFAFA;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 3px solid #D4A574;
}

.story-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.story-title {
  font-weight: 600;
  color: #5D4037;
}

.story-meta {
  font-size: 12px;
  color: #999;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: #FAFAFA;
  border-radius: 6px;
}

.related-info {
  flex: 1;
}

.related-name {
  font-weight: 600;
  color: #3E2723;
  margin-bottom: 4px;
}

.related-note {
  font-size: 12px;
  color: #8B7355;
}

.related-photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.related-photo-item {
  text-align: center;
}

.related-photo-item img,
.related-photo-item .no-photo {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 6px;
  background: #F5E6D3;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #D4A574;
  margin-bottom: 6px;
}

.photo-caption {
  font-size: 12px;
  color: #5D4037;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dispute-item {
  padding: 14px;
  background: #FFF8F0;
  border-radius: 8px;
  margin-bottom: 14px;
  border-left: 4px solid #E74C3C;
}

.dispute-header {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.dispute-field {
  font-weight: 600;
  color: #5D4037;
}

.dispute-date {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.dispute-versions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.version-card {
  flex: 1;
  padding: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #E8D5C4;
}

.version-card.original {
  border-color: #3498DB;
}

.version-card.new {
  border-color: #E74C3C;
}

.version-label {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #666;
}

.version-author {
  font-size: 11px;
  color: #999;
  margin-bottom: 6px;
}

.version-content {
  font-size: 13px;
  color: #333;
  line-height: 1.5;
}

.version-vs {
  font-weight: 600;
  color: #E74C3C;
}

.dispute-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
