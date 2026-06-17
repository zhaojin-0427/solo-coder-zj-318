<template>
  <div class="persons-page">
    <div class="page-header">
      <div class="page-title">
        <el-icon><User /></el-icon>
        人物关系补注
      </div>
      <div class="page-subtitle">合并同一人物的多张照片形成回忆档案，补充别名、迁居信息和亲属关系备注</div>
    </div>

    <div class="content-layout">
      <div class="list-panel card-warm">
        <div class="panel-header">
          <el-input v-model="searchText" placeholder="搜索姓名/别名/出生地..." size="default" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button type="primary" class="btn-primary-warm" @click="showAddPerson = true">
            <el-icon><Plus /></el-icon>建档
          </el-button>
        </div>

        <el-tabs v-model="statusTab" class="status-tabs">
          <el-tab-pane label="全部" name="" />
          <el-tab-pane :label="`待确认 ${counts.pending}`" name="pending" />
          <el-tab-pane :label="`已确认 ${counts.confirmed}`" name="confirmed" />
          <el-tab-pane :label="`有冲突 ${counts.conflicted}`" name="conflicted" />
        </el-tabs>

        <div class="person-list" v-loading="loading">
          <div
            v-for="p in filteredPersons"
            :key="p.id"
            class="person-card"
            :class="{ active: currentPerson?.id === p.id }"
            @click="selectPerson(p)"
          >
            <el-avatar :size="48" :style="{ background: getAvatarBg(p) }">
              {{ p.name.charAt(0) }}
            </el-avatar>
            <div class="person-card-info">
              <div class="person-card-name">
                {{ p.name }}
                <el-tag v-if="p.status === 'confirmed'" size="small" type="success" effect="light">已确认</el-tag>
                <el-tag v-else-if="p.status === 'pending'" size="small" type="warning" effect="light">待确认</el-tag>
                <el-tag v-else size="small" type="danger" effect="light">冲突</el-tag>
              </div>
              <div class="person-card-meta">
                <span v-if="p.birth_year">{{ p.birth_year }}年生</span>
                <span v-if="p.birth_place"> · {{ p.birth_place }}</span>
              </div>
              <div class="person-card-stats">
                <el-tag size="small" effect="plain">📷 {{ p.photo_count || 0 }}张</el-tag>
                <el-tag size="small" effect="plain">📝 {{ p.relationship_count || 0 }}关系</el-tag>
                <el-tag size="small" effect="plain">📜 {{ p.memory_count || 0 }}回忆</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-if="!filteredPersons.length && !loading" description="暂无匹配人物" />
        </div>
      </div>

      <div class="detail-panel card-warm">
        <div v-if="!currentPerson" class="empty-detail">
          <el-icon :size="64" style="color: #D4A574; margin-bottom: 16px;"><UserFilled /></el-icon>
          <div class="empty-title">从左侧选择一位家族成员</div>
          <div class="empty-desc">查看人物档案、补充信息或编辑亲属关系</div>
        </div>
        <div v-else class="person-detail">
          <div class="detail-header">
            <div class="avatar-section">
              <el-avatar :size="88" :style="{ background: getAvatarBg(currentPerson) }">
                {{ currentPerson.name.charAt(0) }}
              </el-avatar>
              <el-dropdown style="margin-top: 8px;">
                <el-button size="small" plain>
                  {{ getStatusLabel(currentPerson.status) }}<el-icon><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="changeStatus('confirmed')">标记为已确认</el-dropdown-item>
                    <el-dropdown-item @click="changeStatus('pending')">标记为待确认</el-dropdown-item>
                    <el-dropdown-item @click="changeStatus('conflicted')">标记为信息冲突</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            <div class="info-section">
              <h2 class="detail-name">{{ currentPerson.name }}</h2>
              <div class="detail-meta-row">
                <el-tag v-if="currentPerson.gender" size="small">
                  {{ currentPerson.gender === 'M' ? '♂ 男' : currentPerson.gender === 'F' ? '♀ 女' : '性别未知' }}
                </el-tag>
                <el-tag v-if="currentPerson.birth_year" size="small" type="info">
                  {{ currentPerson.birth_year }}年生
                </el-tag>
                <el-tag v-if="currentPerson.death_year" size="small" type="danger">
                  {{ currentPerson.death_year }}年逝世
                </el-tag>
                <el-tag v-if="currentPerson.birth_place" size="small" effect="plain">
                  <el-icon><Location /></el-icon> {{ currentPerson.birth_place }}
                </el-tag>
              </div>
              <p class="detail-desc" v-if="currentPerson.description">{{ currentPerson.description }}</p>
              <div class="detail-actions">
                <el-button size="small" @click="showEditPerson = true">
                  <el-icon><Edit /></el-icon>编辑信息
                </el-button>
                <el-button size="small" type="primary" class="btn-primary-warm" @click="showAddRelation = true">
                  <el-icon><Link /></el-icon>添加亲属关系
                </el-button>
              </div>
            </div>
          </div>

          <el-tabs v-model="detailTab">
            <el-tab-pane label="别名/称呼" name="alias">
              <div class="tab-actions">
                <el-button size="small" type="primary" class="btn-primary-warm" @click="showAddAlias = true">
                  <el-icon><Plus /></el-icon>补注别名
                </el-button>
              </div>
              <div v-if="currentPerson.aliases?.length" class="alias-list">
                <div v-for="a in currentPerson.aliases" :key="a.id" class="alias-item">
                  <div class="alias-name">{{ a.alias_name }}</div>
                  <div class="alias-context" v-if="a.usage_context">{{ a.usage_context }}</div>
                  <div class="alias-footer">
                    <el-tag size="small" effect="plain">补注人：{{ a.added_by }}</el-tag>
                  </div>
                </div>
              </div>
              <el-empty v-else description="暂无别名，晚辈可补充乳名、旧时称呼等" />
            </el-tab-pane>

            <el-tab-pane label="迁居轨迹" name="migration">
              <div class="tab-actions">
                <el-button size="small" type="primary" class="btn-primary-warm" @click="showAddMigration = true">
                  <el-icon><Plus /></el-icon>补注迁居
                </el-button>
              </div>
              <div v-if="currentPerson.migrations?.length" class="timeline-wrap">
                <el-timeline>
                  <el-timeline-item
                    v-for="m in sortedMigrations"
                    :key="m.id"
                    :timestamp="m.move_year ? m.move_year + '年' : '年份不详'"
                    placement="top"
                    :type="m.move_year ? 'primary' : 'info'"
                  >
                    <div class="migration-item">
                      <div class="migration-route">
                        <el-tag size="small">{{ m.from_place }}</el-tag>
                        <el-icon style="margin: 0 8px; color: #D2691E;"><Right /></el-icon>
                        <el-tag size="small" type="warning">{{ m.to_place }}</el-tag>
                      </div>
                      <div class="migration-reason" v-if="m.reason">原因：{{ m.reason }}</div>
                      <div class="migration-author">补注人：{{ m.added_by }}</div>
                    </div>
                  </el-timeline-item>
                </el-timeline>
              </div>
              <el-empty v-else description="暂无迁居记录" />
            </el-tab-pane>

            <el-tab-pane :label="`亲属关系 (${relationships.length})`" name="relation">
              <div class="tab-actions">
                <el-button size="small" type="primary" class="btn-primary-warm" @click="showAddRelation = true">
                  <el-icon><Plus /></el-icon>新增关系
                </el-button>
              </div>
              <div v-if="relationships.length" class="relation-list">
                <div v-for="r in relationships" :key="r.id" class="relation-item">
                  <el-avatar :size="40" style="background: linear-gradient(135deg, #8B4513, #D2691E);">
                    {{ getOtherPerson(r).name?.charAt(0) || '?' }}
                  </el-avatar>
                  <div class="relation-info">
                    <div class="relation-main">
                      <span class="relation-person">{{ getOtherPerson(r).name }}</span>
                      <el-tag size="small" type="warning">{{ r.relation_type_display }}</el-tag>
                      <span class="relation-note" v-if="r.relation_note">（{{ r.relation_note }}）</span>
                    </div>
                    <div class="relation-sub">与{{ currentPerson.name }}的关系</div>
                  </div>
                  <el-tag size="small" effect="plain">{{ r.added_by }} 补注</el-tag>
                </div>
              </div>
              <el-empty v-else description="尚未建立亲属关系" />
            </el-tab-pane>

            <el-tab-pane :label="`照片档案 (${personPhotos.length})`" name="photos">
              <div class="photo-archive-grid" v-if="personPhotos.length">
                <div
                  v-for="photo in personPhotos"
                  :key="photo.id"
                  class="archive-photo"
                >
                  <div class="archive-photo-thumb">
                    <img :src="getImageSrc(photo)" v-if="photo.image" />
                    <span class="photo-emoji" v-else>{{ photoPlaceholder(photo.era, photo.scene) }}</span>
                  </div>
                  <div class="archive-photo-info">
                    <div class="archive-photo-title">{{ photo.title || '未命名照片' }}</div>
                    <div class="archive-photo-meta">
                      <el-tag size="small" effect="plain">{{ getOptionLabel(ERA_OPTIONS, photo.era) }}</el-tag>
                      <el-tag size="small" effect="plain" style="margin-left: 4px;">{{ getOptionLabel(SCENE_OPTIONS, photo.scene) }}</el-tag>
                      <span v-if="photo.taken_year" style="margin-left: 6px;">{{ photo.taken_year }}年</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-photo">
                <el-empty description="暂未关联照片，去照片页标注此人物" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAddPerson" title="新建人物档案" width="520px">
      <el-form :model="addPersonForm" label-width="100px">
        <el-form-item label="姓名" required>
          <el-input v-model="addPersonForm.name" placeholder="如：李建国" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="addPersonForm.gender">
            <el-radio value="M">男</el-radio>
            <el-radio value="F">女</el-radio>
            <el-radio value="U">未知</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生年份">
          <el-input-number v-model="addPersonForm.birth_year" :min="1850" :max="2030" />
        </el-form-item>
        <el-form-item label="逝世年份">
          <el-input-number v-model="addPersonForm.death_year" :min="1850" :max="2030" />
        </el-form-item>
        <el-form-item label="出生地">
          <el-input v-model="addPersonForm.birth_place" />
        </el-form-item>
        <el-form-item label="人物简介">
          <el-input v-model="addPersonForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPerson = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitAddPerson">创建档案</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditPerson" title="编辑人物信息" width="520px">
      <el-form :model="editPersonForm" label-width="100px">
        <el-form-item label="姓名"><el-input v-model="editPersonForm.name" /></el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="editPersonForm.gender">
            <el-radio value="M">男</el-radio><el-radio value="F">女</el-radio><el-radio value="U">未知</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生年份"><el-input-number v-model="editPersonForm.birth_year" :min="1850" :max="2030" /></el-form-item>
        <el-form-item label="逝世年份"><el-input-number v-model="editPersonForm.death_year" :min="1850" :max="2030" /></el-form-item>
        <el-form-item label="出生地"><el-input v-model="editPersonForm.birth_place" /></el-form-item>
        <el-form-item label="人物简介"><el-input v-model="editPersonForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditPerson = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitEditPerson">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAddAlias" title="补注别名/称呼" width="480px">
      <el-form :model="aliasForm" label-width="100px">
        <el-form-item label="别名" required>
          <el-input v-model="aliasForm.alias_name" placeholder="如：大毛、阿强、二叔公" />
        </el-form-item>
        <el-form-item label="使用场景">
          <el-input v-model="aliasForm.usage_context" placeholder="如：乳名、旧时称呼、工作用名" />
        </el-form-item>
        <el-form-item label="补注人">
          <el-input v-model="aliasForm.added_by" placeholder="如：长孙、三女儿" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddAlias = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitAddAlias">提交补注</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAddMigration" title="补注迁居信息" width="480px">
      <el-form :model="migrationForm" label-width="100px">
        <el-form-item label="迁出地" required>
          <el-input v-model="migrationForm.from_place" placeholder="如：山东青岛" />
        </el-form-item>
        <el-form-item label="迁入地" required>
          <el-input v-model="migrationForm.to_place" placeholder="如：黑龙江哈尔滨" />
        </el-form-item>
        <el-form-item label="迁居年份">
          <el-input-number v-model="migrationForm.move_year" :min="1850" :max="2030" />
        </el-form-item>
        <el-form-item label="迁居原因">
          <el-input v-model="migrationForm.reason" type="textarea" :rows="2" placeholder="如：闯关东、工作调动、上山下乡" />
        </el-form-item>
        <el-form-item label="补注人">
          <el-input v-model="migrationForm.added_by" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddMigration = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitAddMigration">提交补注</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAddRelation" title="添加亲属关系" width="520px">
      <el-form :model="relationForm" label-width="110px">
        <el-form-item label="对方人物" required>
          <el-select v-model="relationForm.to_person" filterable placeholder="选择亲属" style="width: 100%">
            <el-option
              v-for="p in otherPersons"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关系类型" required>
          <el-select v-model="relationForm.relation_type" placeholder="选择关系" style="width: 100%">
            <el-option v-for="r in RELATION_OPTIONS" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
          <div style="font-size: 12px; color: #8B7355; margin-top: 6px;">
            即：{{ currentPerson?.name || '此人' }} 是 对方的 <b>{{ getRelationLabel() }}</b>
          </div>
        </el-form-item>
        <el-form-item label="详细备注">
          <el-input v-model="relationForm.relation_note" placeholder="如：大舅（母亲的大哥）、二伯母等" />
        </el-form-item>
        <el-form-item label="补注人">
          <el-input v-model="relationForm.added_by" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddRelation = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitAddRelation">保存关系</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User, Search, Plus, UserFilled, Location, Edit, Link, ArrowDown, Right
} from '@element-plus/icons-vue'
import { persons as personsApi, relationships as relApi, aliases as aliasApi, migrations as migApi, personInPhoto as pipApi, photos as photosApi } from '@/api'
import { RELATION_OPTIONS, STATUS_OPTIONS, ERA_OPTIONS, SCENE_OPTIONS, getOptionLabel, photoPlaceholder } from '@/store'

const loading = ref(false)
const personList = ref([])
const searchText = ref('')
const statusTab = ref('')
const currentPerson = ref(null)
const detailTab = ref('alias')
const relationships = ref([])
const personPhotos = ref([])

const showAddPerson = ref(false)
const showEditPerson = ref(false)
const showAddAlias = ref(false)
const showAddMigration = ref(false)
const showAddRelation = ref(false)

const addPersonForm = ref({ name: '', gender: 'U', birth_year: null, death_year: null, birth_place: '', description: '' })
const editPersonForm = ref({})
const aliasForm = ref({ alias_name: '', usage_context: '', added_by: '晚辈' })
const migrationForm = ref({ from_place: '', to_place: '', move_year: null, reason: '', added_by: '晚辈' })
const relationForm = ref({ to_person: null, relation_type: '', relation_note: '', added_by: '家属' })

const counts = computed(() => ({
  pending: personList.value.filter(p => p.status === 'pending').length,
  confirmed: personList.value.filter(p => p.status === 'confirmed').length,
  conflicted: personList.value.filter(p => p.status === 'conflicted').length
}))

const filteredPersons = computed(() => {
  let r = personList.value
  if (statusTab.value) r = r.filter(p => p.status === statusTab.value)
  if (searchText.value) {
    const kw = searchText.value.toLowerCase()
    r = r.filter(p =>
      p.name.toLowerCase().includes(kw) ||
      (p.birth_place || '').toLowerCase().includes(kw) ||
      (p.aliases || []).some(a => (a.alias_name || '').toLowerCase().includes(kw))
    )
  }
  return r
})

const otherPersons = computed(() => personList.value.filter(p => p.id !== currentPerson.value?.id))
const sortedMigrations = computed(() => {
  return [...(currentPerson.value?.migrations || [])].sort((a, b) => (a.move_year || 9999) - (b.move_year || 9999))
})

const getAvatarBg = (p) => {
  const map = { confirmed: 'linear-gradient(135deg, #10B981, #059669)', pending: 'linear-gradient(135deg, #F59E0B, #D97706)', conflicted: 'linear-gradient(135deg, #EF4444, #DC2626)' }
  return map[p.status] || map.pending
}

const getStatusLabel = (s) => getOptionLabel(STATUS_OPTIONS, s)
const getOtherPerson = (r) => {
  if (r.from_person === currentPerson.value?.id) {
    return { name: r.to_person_name, id: r.to_person }
  }
  return { name: r.from_person_name, id: r.from_person }
}

const getRelationLabel = () => getOptionLabel(RELATION_OPTIONS, relationForm.value.relation_type)

const getImageSrc = (photo) => {
  if (!photo.image) return ''
  if (typeof photo.image === 'string' && photo.image.startsWith('http')) return photo.image
  if (typeof photo.image === 'string' && photo.image.startsWith('/media')) return photo.image
  if (typeof photo.image === 'string') return '/media/' + photo.image
  return ''
}

const loadPersonPhotos = async () => {
  if (!currentPerson.value) { personPhotos.value = []; return }
  try {
    const pipRes = await pipApi.list({ person: currentPerson.value.id })
    const pipList = pipRes.results || pipRes || []
    if (!pipList.length) { personPhotos.value = mockPersonPhotos(currentPerson.value.id); return }
    const photoIds = pipList.map(p => p.photo).filter(Boolean)
    if (!photoIds.length) { personPhotos.value = []; return }
    const photoPromises = photoIds.map(id =>
      photosApi.get(id).catch(() => null)
    )
    const results = await Promise.all(photoPromises)
    personPhotos.value = results.filter(Boolean)
  } catch (e) {
    personPhotos.value = mockPersonPhotos(currentPerson.value.id)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await personsApi.list({ page_size: 200 })
    personList.value = res.results || mockPersons()
  } catch (e) {
    personList.value = mockPersons()
  } finally {
    loading.value = false
  }
}

const selectPerson = async (p) => {
  try {
    const detail = await personsApi.get(p.id)
    currentPerson.value = detail
  } catch (e) {
    currentPerson.value = enrichPerson(p)
  }
  loadRelationships()
  loadPersonPhotos()
  detailTab.value = 'alias'
}

const loadRelationships = async () => {
  try {
    const res = await relApi.list({ from_person: currentPerson.value.id })
    const res2 = await relApi.list({ to_person: currentPerson.value.id })
    relationships.value = [...(res.results || []), ...(res2.results || [])]
  } catch (e) {
    relationships.value = mockRelations(currentPerson.value.id)
  }
}

const changeStatus = async (status) => {
  try {
    await personsApi.patch(currentPerson.value.id, { status })
    ElMessage.success('状态已更新')
    currentPerson.value.status = status
    loadData()
  } catch (e) {
    currentPerson.value.status = status
    personList.value.find(p => p.id === currentPerson.value.id).status = status
    ElMessage.success('状态已更新（模拟）')
  }
}

const submitAddPerson = async () => {
  if (!addPersonForm.value.name) {
    ElMessage.warning('请输入姓名')
    return
  }
  try {
    const res = await personsApi.create(addPersonForm.value)
    personList.value.unshift(res)
    ElMessage.success('人物档案已创建')
  } catch (e) {
    personList.value.unshift({ id: Date.now(), ...addPersonForm.value, status: 'pending', aliases: [], migrations: [], photo_count: 0, relationship_count: 0, memory_count: 0 })
    ElMessage.success('人物档案已创建（模拟）')
  }
  showAddPerson.value = false
}

watch(showEditPerson, (v) => {
  if (v && currentPerson.value) {
    editPersonForm.value = { ...currentPerson.value }
  }
})

const submitEditPerson = async () => {
  try {
    const res = await personsApi.update(currentPerson.value.id, editPersonForm.value)
    Object.assign(currentPerson.value, res)
    ElMessage.success('已保存')
  } catch (e) {
    Object.assign(currentPerson.value, editPersonForm.value)
    ElMessage.success('已保存（模拟）')
  }
  showEditPerson.value = false
  loadData()
}

const submitAddAlias = async () => {
  if (!aliasForm.value.alias_name) { ElMessage.warning('请输入别名'); return }
  try {
    const res = await personsApi.addAlias(currentPerson.value.id, aliasForm.value)
    if (!currentPerson.value.aliases) currentPerson.value.aliases = []
    currentPerson.value.aliases.push(res)
    ElMessage.success('别名已补注')
  } catch (e) {
    if (!currentPerson.value.aliases) currentPerson.value.aliases = []
    currentPerson.value.aliases.push({ id: Date.now(), ...aliasForm.value })
    ElMessage.success('别名已补注（模拟）')
  }
  showAddAlias.value = false
  aliasForm.value = { alias_name: '', usage_context: '', added_by: '晚辈' }
}

const submitAddMigration = async () => {
  if (!migrationForm.value.from_place || !migrationForm.value.to_place) {
    ElMessage.warning('请填写迁出地和迁入地'); return
  }
  try {
    const res = await personsApi.addMigration(currentPerson.value.id, migrationForm.value)
    if (!currentPerson.value.migrations) currentPerson.value.migrations = []
    currentPerson.value.migrations.push(res)
    ElMessage.success('迁居信息已补注')
  } catch (e) {
    if (!currentPerson.value.migrations) currentPerson.value.migrations = []
    currentPerson.value.migrations.push({ id: Date.now(), ...migrationForm.value })
    ElMessage.success('迁居信息已补注（模拟）')
  }
  showAddMigration.value = false
  migrationForm.value = { from_place: '', to_place: '', move_year: null, reason: '', added_by: '晚辈' }
}

const submitAddRelation = async () => {
  if (!relationForm.value.to_person || !relationForm.value.relation_type) {
    ElMessage.warning('请完善亲属关系'); return
  }
  const data = {
    from_person: currentPerson.value.id,
    to_person: relationForm.value.to_person,
    relation_type: relationForm.value.relation_type,
    relation_note: relationForm.value.relation_note,
    added_by: relationForm.value.added_by
  }
  try {
    const res = await relApi.create(data)
    relationships.value.push({ ...res, to_person_name: otherPersons.value.find(p => p.id === res.to_person)?.name })
    ElMessage.success('亲属关系已添加')
  } catch (e) {
    const other = otherPersons.value.find(p => p.id === relationForm.value.to_person)
    relationships.value.push({
      id: Date.now(), ...data,
      relation_type_display: getRelationLabel(),
      to_person_name: other?.name
    })
    ElMessage.success('亲属关系已添加（模拟）')
  }
  showAddRelation.value = false
  relationForm.value = { to_person: null, relation_type: '', relation_note: '', added_by: '家属' }
}

onMounted(loadData)
</script>

<script>
function mockPersons() {
  return [
    { id: 1, name: '李大山', gender: 'M', birth_year: 1915, death_year: 1998, birth_place: '山东青岛', description: '家族第一代，年轻时闯关东到东北，后在沈阳定居。开过铁匠铺，为人正直豪爽。', status: 'confirmed', aliases: [{ id: 1, alias_name: '老铁匠', usage_context: '街坊称呼', added_by: '长孙' }, { id: 2, alias_name: '大山哥', usage_context: '同辈称呼', added_by: '三姑' }], migrations: [{ id: 1, from_place: '山东青岛', to_place: '辽宁沈阳', move_year: 1934, reason: '闯关东谋生', added_by: '长孙' }], relationship_count: 6, photo_count: 5, memory_count: 3 },
    { id: 2, name: '王秀兰', gender: 'F', birth_year: 1922, death_year: 2010, birth_place: '辽宁沈阳', description: '典型的东北妇女，养育了5个子女，一手好针线活。', status: 'confirmed', aliases: [{ id: 3, alias_name: '秀兰妹子', usage_context: '年轻时', added_by: '大姑' }], migrations: [], relationship_count: 6, photo_count: 6, memory_count: 4 },
    { id: 3, name: '李建国', gender: 'M', birth_year: 1948, death_year: null, birth_place: '辽宁沈阳', description: '长子，18岁参军，后转业到天津纺织厂当干部。', status: 'confirmed', aliases: [{ id: 4, alias_name: '大民子', usage_context: '乳名', added_by: '二弟' }], migrations: [{ id: 2, from_place: '辽宁沈阳', to_place: '天津', move_year: 1970, reason: '部队转业分配', added_by: '长子' }], relationship_count: 4, photo_count: 8, memory_count: 5 },
    { id: 4, name: '李建华', gender: 'M', birth_year: 1952, death_year: null, birth_place: '辽宁沈阳', description: '二儿子，下乡知青，后回城在国企工作。', status: 'confirmed', aliases: [{ id: 5, alias_name: '二华', usage_context: '家中排行', added_by: '三弟' }], migrations: [{ id: 3, from_place: '辽宁沈阳', to_place: '黑龙江北大荒', move_year: 1969, reason: '上山下乡', added_by: '本人' }, { id: 4, from_place: '黑龙江北大荒', to_place: '辽宁沈阳', move_year: 1978, reason: '知青返城', added_by: '本人' }], relationship_count: 4, photo_count: 4, memory_count: 2 },
    { id: 5, name: '李建梅', gender: 'F', birth_year: 1955, death_year: null, birth_place: '辽宁沈阳', description: '大女儿，嫁给本地张家。', status: 'pending', aliases: [], migrations: [], relationship_count: 3, photo_count: 3, memory_count: 1 },
    { id: 6, name: '张桂芬', gender: 'F', birth_year: 1958, death_year: null, birth_place: '天津', description: '长媳，李建国的妻子。', status: 'confirmed', aliases: [{ id: 6, alias_name: '大芬', usage_context: '婆家称呼', added_by: '小姑子' }], migrations: [], relationship_count: 3, photo_count: 5, memory_count: 2 },
    { id: 7, name: '李明', gender: 'M', birth_year: 1985, death_year: null, birth_place: '天津', description: '长孙，李建国与张桂芬之子。', status: 'pending', aliases: [{ id: 7, alias_name: '明明', usage_context: '乳名', added_by: '奶奶' }], migrations: [], relationship_count: 4, photo_count: 10, memory_count: 3 },
    { id: 8, name: '未知老人', gender: 'U', birth_year: null, death_year: null, birth_place: '', description: '老照片中出现，背面有模糊字迹，疑似李大山的弟弟。', status: 'conflicted', aliases: [], migrations: [], relationship_count: 0, photo_count: 2, memory_count: 0 }
  ]
}

function enrichPerson(p) {
  const full = mockPersons().find(x => x.id === p.id)
  return full || { ...p, aliases: [], migrations: [], relationship_count: 0, photo_count: 0, memory_count: 0 }
}

function mockRelations(personId) {
  const rels = {
    1: [
      { id: 101, from_person: 1, to_person: 2, relation_type: 'spouse', relation_type_display: '配偶', relation_note: '结发夫妻', to_person_name: '王秀兰', added_by: '长孙' },
      { id: 102, from_person: 1, to_person: 3, relation_type: 'child', relation_type_display: '子女', relation_note: '长子', to_person_name: '李建国', added_by: '长孙' },
      { id: 103, from_person: 1, to_person: 4, relation_type: 'child', relation_type_display: '子女', relation_note: '次子', to_person_name: '李建华', added_by: '长孙' },
      { id: 104, from_person: 1, to_person: 5, relation_type: 'child', relation_type_display: '子女', relation_note: '长女', to_person_name: '李建梅', added_by: '长孙' }
    ],
    3: [
      { id: 201, from_person: 1, to_person: 3, relation_type: 'father', relation_type_display: '父亲', relation_note: '', from_person_name: '李大山', added_by: '本人' },
      { id: 202, from_person: 2, to_person: 3, relation_type: 'mother', relation_type_display: '母亲', relation_note: '', from_person_name: '王秀兰', added_by: '本人' },
      { id: 203, from_person: 3, to_person: 6, relation_type: 'spouse', relation_type_display: '配偶', relation_note: '', to_person_name: '张桂芬', added_by: '本人' },
      { id: 204, from_person: 3, to_person: 7, relation_type: 'child', relation_type_display: '子女', relation_note: '独子', to_person_name: '李明', added_by: '本人' }
    ],
    7: [
      { id: 301, from_person: 3, to_person: 7, relation_type: 'father', relation_type_display: '父亲', relation_note: '', from_person_name: '李建国', added_by: '本人' },
      { id: 302, from_person: 6, to_person: 7, relation_type: 'mother', relation_type_display: '母亲', relation_note: '', from_person_name: '张桂芬', added_by: '本人' },
      { id: 303, from_person: 1, to_person: 7, relation_type: 'grandparent', relation_type_display: '祖父母', relation_note: '爷爷', from_person_name: '李大山', added_by: '本人' },
      { id: 304, from_person: 2, to_person: 7, relation_type: 'grandparent', relation_type_display: '祖父母', relation_note: '奶奶', from_person_name: '王秀兰', added_by: '本人' }
    ]
  }
  return rels[personId] || []
}

function mockPersonPhotos(personId) {
  const mockPhotoData = [
    { id: 1, title: '1952年父亲参军留影', image: null, era: '1950s', scene: 'military', taken_year: 1952 },
    { id: 2, title: '1968年春节全家福', image: null, era: '1960s', scene: 'family_portrait', taken_year: 1968 },
    { id: 3, title: '母亲年轻时的工作照', image: null, era: '1970s', scene: 'work_school', taken_year: 1975 },
    { id: 4, title: '1985年大哥结婚', image: null, era: '1980s', scene: 'wedding', taken_year: 1985 },
    { id: 5, title: '90年代初第一次去北京', image: null, era: '1990s', scene: 'travel', taken_year: 1992 },
    { id: 6, title: '2005年家族大聚会', image: null, era: '2000s', scene: 'festival', taken_year: 2005 },
    { id: 7, title: '我小时候和外公', image: null, era: '1990s', scene: 'childhood', taken_year: 1995 },
    { id: 9, title: '奶奶少女时代', image: null, era: '1930s', scene: 'daily_life', taken_year: 1938 }
  ]
  const photoMap = {
    1: [2, 5, 6, 9],
    2: [2, 5, 6, 9],
    3: [1, 2, 4, 5, 6, 7],
    4: [2, 6],
    5: [2],
    6: [4, 6],
    7: [4, 5, 6, 7],
    8: [10]
  }
  const ids = photoMap[personId] || []
  return mockPhotoData.filter(p => ids.includes(p.id))
}
</script>

<style scoped>
.content-layout {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
  align-items: start;
}

.list-panel {
  padding: 16px;
  max-height: calc(100vh - 260px);
  overflow-y: auto;
}

.panel-header {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.panel-header .el-input { flex: 1; }

.status-tabs {
  margin-bottom: 12px;
}

.person-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.person-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid #E8D8C4;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background: #FFFAF0;
}

.person-card:hover {
  background: #FFF5E6;
  border-color: #D4A574;
}

.person-card.active {
  background: linear-gradient(135deg, #FEF3E2, #FFE4C4);
  border-color: #D2691E;
  box-shadow: 0 2px 10px rgba(210, 105, 30, 0.15);
}

.person-card-info { flex: 1; min-width: 0; }

.person-card-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.person-card-meta {
  font-size: 12px;
  color: #8B7355;
  margin-bottom: 6px;
}

.person-card-stats {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
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

.detail-meta-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.detail-desc {
  color: #5D4E3A;
  line-height: 1.8;
  margin-bottom: 16px;
}

.detail-actions {
  display: flex;
  gap: 10px;
}

.tab-actions {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}

.alias-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.alias-item {
  padding: 14px;
  background: #FFFAF0;
  border: 1px solid #E8D8C4;
  border-radius: 10px;
}

.alias-name {
  font-size: 16px;
  font-weight: 600;
  color: #8B4513;
  margin-bottom: 6px;
}

.alias-context {
  font-size: 13px;
  color: #8B7355;
  margin-bottom: 8px;
}

.alias-footer { font-size: 12px; }

.timeline-wrap {
  padding: 0 12px;
}

.migration-item {
  padding: 10px 0;
}

.migration-route {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  font-weight: 600;
}

.migration-reason {
  color: #5D4E3A;
  font-size: 13px;
  margin-bottom: 4px;
}

.migration-author {
  font-size: 12px;
  color: #B5A48C;
}

.relation-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.relation-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px 14px;
  background: #FFFAF0;
  border: 1px solid #E8D8C4;
  border-radius: 10px;
}

.relation-info { flex: 1; }

.relation-main {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  margin-bottom: 4px;
}

.relation-person {
  font-weight: 600;
  color: #8B4513;
}

.relation-note { color: #5D4E3A; font-size: 13px; }

.relation-sub {
  font-size: 12px;
  color: #B5A48C;
}

.photo-archive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 14px;
}

.archive-photo {
  background: #FFFAF0;
  border: 1px solid #E8D8C4;
  border-radius: 10px;
  overflow: hidden;
}

.archive-photo-thumb {
  height: 120px;
  background: linear-gradient(135deg, #F5F0E6, #E8D8C4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  overflow: hidden;
}

.archive-photo-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.archive-photo-thumb .photo-emoji {
  font-size: 60px;
  opacity: 0.6;
}

.archive-photo-info { padding: 10px 12px; }

.archive-photo-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.archive-photo-meta {
  font-size: 12px;
  color: #8B7355;
}

.empty-photo {
  grid-column: 1 / -1;
}
</style>
