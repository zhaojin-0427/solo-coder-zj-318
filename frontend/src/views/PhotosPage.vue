<template>
  <div class="photos-page">
    <div class="page-header">
      <div class="page-title">
        <el-icon><Picture /></el-icon>
        照片归档
      </div>
      <div class="page-subtitle">按年代、场景、来源分组整理家族老照片，为后续人物补注和故事沉淀奠定基础</div>
    </div>

    <div class="card-warm" style="padding: 20px; margin-bottom: 20px;">
      <div class="filter-row">
        <el-input v-model="searchText" placeholder="搜索照片标题、地点、描述..." style="width: 280px;" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterEra" placeholder="按年代" clearable style="width: 140px">
          <el-option v-for="era in ERA_OPTIONS" :key="era.value" :label="era.label" :value="era.value" />
        </el-select>
        <el-select v-model="filterScene" placeholder="按场景" clearable style="width: 140px">
          <el-option v-for="s in SCENE_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="filterSource" placeholder="按来源" clearable style="width: 140px">
          <el-option v-for="s in SOURCE_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="补注状态" clearable style="width: 140px">
          <el-option v-for="s in PHOTO_STATUS_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-button type="primary" class="btn-primary-warm" @click="showUpload = true">
          <el-icon><Upload /></el-icon>上传照片
        </el-button>
      </div>
    </div>

    <div class="era-group-header" v-if="groupedPhotos.length">
      <div class="era-summary" v-for="group in eraSummary" :key="group.era">
        <span class="era-label">{{ group.label }}</span>
        <span class="era-count">{{ group.count }}张</span>
      </div>
    </div>

    <div v-if="loading" class="card-warm" style="padding: 40px; text-align: center;">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <div style="margin-top: 12px; color: #8B7355;">加载中...</div>
    </div>

    <div v-else-if="!filteredPhotos.length" class="card-warm empty-warm">
      <el-icon :size="48" style="color: #D4A574; margin-bottom: 12px;"><PictureFilled /></el-icon>
      <div>还没有上传照片</div>
      <div style="font-size: 13px; margin-top: 8px;">点击"上传照片"按钮开始家族记忆整理之旅</div>
    </div>

    <div v-else>
      <template v-for="group in groupedPhotos" :key="group.era">
        <div class="era-section" v-if="group.photos.length">
          <div class="era-section-header">
            <h3>{{ group.label }}</h3>
            <el-tag size="small">{{ group.photos.length }} 张</el-tag>
          </div>
          <div class="photo-grid">
            <div
              v-for="photo in group.photos"
              :key="photo.id"
              class="photo-card"
              @click="openDetail(photo)"
            >
              <div class="photo-thumb">
                <img :src="getImageSrc(photo)" v-if="photo.image" />
                <span class="photo-emoji" v-else>{{ photoPlaceholder(photo.era, photo.scene) }}</span>
              </div>
              <div class="photo-info">
                <div class="photo-title">{{ photo.title || '未命名照片' }}</div>
                <div class="photo-meta">
                  <el-tag size="small" class="tag-era">{{ getOptionLabel(ERA_OPTIONS, photo.era) }}</el-tag>
                  <el-tag size="small" class="tag-scene">{{ getOptionLabel(SCENE_OPTIONS, photo.scene) }}</el-tag>
                </div>
                <div class="photo-footer">
                  <span>
                    <el-icon><User /></el-icon>
                    {{ photo.person_count || 0 }}人
                  </span>
                  <el-tag size="small" :type="getPhotoStatusType(photo.status)" effect="light">
                    {{ getOptionLabel(PHOTO_STATUS_OPTIONS, photo.status) }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <el-dialog v-model="showUpload" title="上传照片" width="560px" destroy-on-close>
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="照片上传">
          <el-upload
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖放照片到此处或<em>点击选择</em></div>
            <template #tip>
              <div class="el-upload__tip">支持 JPG/PNG 格式</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="照片标题">
          <el-input v-model="uploadForm.title" placeholder="如：1985年春节全家福" />
        </el-form-item>
        <el-form-item label="拍摄年代">
          <el-select v-model="uploadForm.era" style="width: 100%">
            <el-option v-for="era in ERA_OPTIONS" :key="era.value" :label="era.label" :value="era.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="照片场景">
          <el-select v-model="uploadForm.scene" style="width: 100%">
            <el-option v-for="s in SCENE_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="照片来源">
          <el-select v-model="uploadForm.source" style="width: 100%">
            <el-option v-for="s in SOURCE_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="拍摄年份">
          <el-input-number v-model="uploadForm.taken_year" :min="1900" :max="2030" placeholder="选填" />
        </el-form-item>
        <el-form-item label="拍摄地点">
          <el-input v-model="uploadForm.location" placeholder="如：北京西城区老宅院" />
        </el-form-item>
        <el-form-item label="事件背景">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="老人口述：当时是爷爷六十大寿，全家从各地赶回来..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitUpload">保存归档</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetail" :title="currentPhoto?.title || '照片详情'" width="900px" destroy-on-close>
      <div v-if="currentPhoto" class="photo-detail">
        <div class="detail-content">
          <div class="detail-image-section">
            <div class="detail-image">
              <img :src="getImageSrc(currentPhoto)" v-if="currentPhoto.image" />
              <span class="photo-emoji big" v-else>{{ photoPlaceholder(currentPhoto.era, currentPhoto.scene) }}</span>
            </div>
            <div class="detail-tags">
              <el-tag class="tag-era" size="large"><el-icon><Clock /></el-icon> {{ getOptionLabel(ERA_OPTIONS, currentPhoto.era) }}</el-tag>
              <el-tag class="tag-scene" size="large"><el-icon><Location /></el-icon> {{ getOptionLabel(SCENE_OPTIONS, currentPhoto.scene) }}</el-tag>
              <el-tag class="tag-source" size="large"><el-icon><Folder /></el-icon> {{ getOptionLabel(SOURCE_OPTIONS, currentPhoto.source) }}</el-tag>
              <el-tag v-if="currentPhoto.taken_year" type="info" size="large">{{ currentPhoto.taken_year }}年</el-tag>
              <el-tag v-if="currentPhoto.location" type="info" size="large"><el-icon><LocationFilled /></el-icon> {{ currentPhoto.location }}</el-tag>
            </div>
          </div>
          <div class="detail-info-section">
            <div class="section-block">
              <div class="section-title">事件背景（老人口述）</div>
              <div class="section-content" v-if="currentPhoto.description">{{ currentPhoto.description }}</div>
              <div v-else class="empty-note">暂无口述记录，点击编辑补充</div>
            </div>
            <div class="section-block">
              <div class="section-title" style="display: flex; justify-content: space-between; align-items: center;">
                <span>照片人物标注</span>
                <el-button size="small" type="primary" plain @click="showAddPerson = true">
                  <el-icon><Plus /></el-icon>标注人物
                </el-button>
              </div>
              <div v-if="currentPhoto.people_in_photo?.length" class="people-list">
                <div v-for="pip in currentPhoto.people_in_photo" :key="pip.id" class="person-item">
                  <el-avatar :size="36" :style="{ background: avatarBg(pip) }">
                    {{ getPersonInitial(pip) }}
                  </el-avatar>
                  <div class="person-info">
                    <div class="person-name">
                      <span v-if="pip.person_detail" :class="{'confirmed': true}">
                        {{ pip.person_detail.name }}
                        <el-tag size="small" type="success" effect="light">已关联</el-tag>
                      </span>
                      <span v-else class="pending-name">{{ pip.person_name_override || '待确认人物' }}</span>
                    </div>
                    <div class="person-meta">
                      <el-tag v-if="pip.position_note" size="small" type="info">{{ pip.position_note }}</el-tag>
                      <el-tag v-if="pip.old_title" size="small" effect="plain" style="background: #FEF3E2;">
                        当时称呼: {{ pip.old_title }}
                      </el-tag>
                      <el-tag v-if="pip.role_note" size="small" type="warning" effect="light">{{ pip.role_note }}</el-tag>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-note">还没有标注人物，邀请家属一起认人补注</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetail = false">关闭</el-button>
        <el-button type="primary" class="btn-primary-warm">编辑照片信息</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAddPerson" title="标注照片中的人物" width="520px" destroy-on-close>
      <el-form :model="addPersonForm" label-width="110px">
        <el-form-item label="关联已知人物">
          <el-select v-model="addPersonForm.person" placeholder="选择已建档人物（选填）" filterable style="width: 100%" clearable>
            <el-option v-for="p in allPersons" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="暂用名">
          <el-input v-model="addPersonForm.person_name_override" placeholder="人物未确认时填写，如：前排左一老人" />
        </el-form-item>
        <el-form-item label="位置说明">
          <el-input v-model="addPersonForm.position_note" placeholder="如：前排左一、后排中间、母亲旁边等" />
        </el-form-item>
        <el-form-item label="当时称呼">
          <el-input v-model="addPersonForm.old_title" placeholder="拍摄时的称呼，如：小妹、阿强、二叔公等" />
        </el-form-item>
        <el-form-item label="角色/备注">
          <el-input v-model="addPersonForm.role_note" placeholder="如：刚从部队回来、怀孕6个月、当年10岁等" />
        </el-form-item>
        <el-form-item label="标注人">
          <el-input v-model="addPersonForm.added_by" placeholder="您的称呼，如：长孙、三女儿等" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPerson = false">取消</el-button>
        <el-button type="primary" class="btn-primary-warm" @click="submitAddPerson">添加标注</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Picture, Search, Upload, Loading, PictureFilled, Clock, Folder,
  Location, LocationFilled, Plus, User, UploadFilled
} from '@element-plus/icons-vue'
import { photos as photosApi, persons as personsApi } from '@/api'
import {
  ERA_OPTIONS, SCENE_OPTIONS, SOURCE_OPTIONS, PHOTO_STATUS_OPTIONS,
  getOptionLabel, photoPlaceholder
} from '@/store'

const loading = ref(false)
const photoList = ref([])
const allPersons = ref([])
const searchText = ref('')
const filterEra = ref('')
const filterScene = ref('')
const filterSource = ref('')
const filterStatus = ref('')
const showUpload = ref(false)
const showDetail = ref(false)
const showAddPerson = ref(false)
const currentPhoto = ref(null)

const uploadForm = ref({
  title: '', era: 'unknown', scene: 'other', source: 'old_album',
  taken_year: null, location: '', description: ''
})
const uploadFile = ref(null)

const addPersonForm = ref({
  person: null, person_name_override: '', position_note: '',
  old_title: '', role_note: '', added_by: ''
})

const getImageSrc = (photo) => {
  if (!photo.image) return ''
  if (typeof photo.image === 'string' && photo.image.startsWith('http')) return photo.image
  if (typeof photo.image === 'string' && photo.image.startsWith('/media')) return photo.image
  if (typeof photo.image === 'string') return '/media/' + photo.image
  return typeof photo.image === 'string' ? photo.image : ''
}

const avatarBg = (pip) => {
  if (pip.person_detail) return 'linear-gradient(135deg, #10B981, #059669)'
  return 'linear-gradient(135deg, #F59E0B, #D97706)'
}

const getPersonInitial = (pip) => {
  const name = pip.person_detail?.name || pip.person_name_override || '?'
  return name.charAt(0)
}

const getPhotoStatusType = (status) => {
  const map = { archived: 'info', annotating: 'warning', completed: 'success' }
  return map[status] || 'info'
}

const filteredPhotos = computed(() => {
  let result = photoList.value.length ? photoList.value : mockPhotos()
  if (searchText.value) {
    const kw = searchText.value.toLowerCase()
    result = result.filter(p =>
      (p.title || '').toLowerCase().includes(kw) ||
      (p.description || '').toLowerCase().includes(kw) ||
      (p.location || '').toLowerCase().includes(kw)
    )
  }
  if (filterEra.value) result = result.filter(p => p.era === filterEra.value)
  if (filterScene.value) result = result.filter(p => p.scene === filterScene.value)
  if (filterSource.value) result = result.filter(p => p.source === filterSource.value)
  if (filterStatus.value) result = result.filter(p => p.status === filterStatus.value)
  return result
})

const groupedPhotos = computed(() => {
  const groups = ERA_OPTIONS.map(era => ({
    era: era.value,
    label: era.label,
    photos: filteredPhotos.value.filter(p => p.era === era.value)
  }))
  const unknown = { era: 'unknown', label: '年代不详', photos: filteredPhotos.value.filter(p => p.era === 'unknown') }
  return [...groups, unknown].filter(g => g.photos.length > 0)
})

const eraSummary = computed(() => {
  return ERA_OPTIONS.map(era => ({
    era: era.value,
    label: era.label,
    count: filteredPhotos.value.filter(p => p.era === era.value).length
  })).concat([{ era: 'unknown', label: '年代不详', count: filteredPhotos.value.filter(p => p.era === 'unknown').length }])
})

const loadData = async () => {
  loading.value = true
  try {
    const [pList, personList] = await Promise.all([
      photosApi.list({ page_size: 200 }).catch(() => ({ results: mockPhotos() })),
      personsApi.simple().catch(() => mockPersons())
    ])
    photoList.value = pList.results || pList || mockPhotos()
    allPersons.value = personList.results || personList || mockPersons()
  } catch (e) {
    photoList.value = mockPhotos()
    allPersons.value = mockPersons()
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file) => {
  uploadFile.value = file.raw
}

const submitUpload = async () => {
  try {
    const formData = new FormData()
    Object.keys(uploadForm.value).forEach(k => {
      if (uploadForm.value[k] !== null && uploadForm.value[k] !== '') {
        formData.append(k, uploadForm.value[k])
      }
    })
    if (uploadFile.value) formData.append('image', uploadFile.value)
    formData.append('status', 'archived')
    formData.append('uploader', '家属')
    const res = await photosApi.create(formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('照片已归档！')
    photoList.value.unshift(res)
    showUpload.value = false
    uploadForm.value = { title: '', era: 'unknown', scene: 'other', source: 'old_album', taken_year: null, location: '', description: '' }
    uploadFile.value = null
  } catch (e) {
    photoList.value.unshift({
      id: Date.now(),
      ...uploadForm.value,
      image: null,
      status: 'archived',
      uploader: '家属',
      created_at: new Date().toISOString(),
      person_count: 0,
      people_in_photo: []
    })
    ElMessage.success('照片已归档（模拟模式）！')
    showUpload.value = false
  }
  loadData()
}

const openDetail = async (photo) => {
  try {
    const detail = await photosApi.get(photo.id)
    currentPhoto.value = detail
  } catch (e) {
    currentPhoto.value = { ...photo, people_in_photo: mockPeopleInPhoto(photo.id) }
  }
  showDetail.value = true
}

const submitAddPerson = async () => {
  if (!addPersonForm.value.person && !addPersonForm.value.person_name_override) {
    ElMessage.warning('请选择关联人物或填写暂用名')
    return
  }
  try {
    await photosApi.addPerson(currentPhoto.value.id, addPersonForm.value)
    ElMessage.success('人物标注已添加！')
  } catch (e) {
    const newPip = {
      id: Date.now(),
      photo: currentPhoto.value.id,
      person: addPersonForm.value.person,
      person_detail: allPersons.value.find(p => p.id === addPersonForm.value.person) || null,
      person_name_override: addPersonForm.value.person_name_override,
      position_note: addPersonForm.value.position_note,
      old_title: addPersonForm.value.old_title,
      role_note: addPersonForm.value.role_note,
      added_by: addPersonForm.value.added_by
    }
    if (!currentPhoto.value.people_in_photo) currentPhoto.value.people_in_photo = []
    currentPhoto.value.people_in_photo.push(newPip)
    ElMessage.success('人物标注已添加（模拟模式）！')
  }
  showAddPerson.value = false
  addPersonForm.value = { person: null, person_name_override: '', position_note: '', old_title: '', role_note: '', added_by: '' }
}

onMounted(loadData)
</script>

<script>
function mockPhotos() {
  return [
    { id: 1, title: '1952年父亲参军留影', image: null, era: '1950s', scene: 'military', source: 'old_album', taken_year: 1952, location: '辽宁沈阳', description: '父亲当年18岁，刚刚入伍，穿着借来的军装照的第一张照片。奶奶说这张照片她藏在枕头底下好几年。', status: 'completed', uploader: '长孙', person_count: 1, people_in_photo: [] },
    { id: 2, title: '1968年春节全家福', image: null, era: '1960s', scene: 'family_portrait', source: 'scanned', taken_year: 1968, location: '山东青岛老家', description: '爷爷奶奶带着5个孩子，那年二叔刚从农村插队回来，全家好不容易凑齐。', status: 'annotating', uploader: '大姑', person_count: 7, people_in_photo: [] },
    { id: 3, title: '母亲年轻时的工作照', image: null, era: '1970s', scene: 'work_school', source: 'old_album', taken_year: 1975, location: '天津纺织厂', description: '妈妈在车间当检验员，连年的三八红旗手。', status: 'archived', uploader: '二舅', person_count: 1, people_in_photo: [] },
    { id: 4, title: '1985年大哥结婚', image: null, era: '1980s', scene: 'wedding', source: 'old_album', taken_year: 1985, location: '老家四合院', description: '那时候结婚还是在家办酒席，请了街坊四邻一共12桌。', status: 'annotating', uploader: '三妹', person_count: 15, people_in_photo: [] },
    { id: 5, title: '90年代初第一次去北京', image: null, era: '1990s', scene: 'travel', source: 'family_donation', taken_year: 1992, location: '北京天安门', description: '爸妈金婚旅行，第一次坐火车出远门。', status: 'archived', uploader: '二姐', person_count: 2, people_in_photo: [] },
    { id: 6, title: '2005年家族大聚会', image: null, era: '2000s', scene: 'festival', source: 'digital_camera', taken_year: 2005, location: '上海某酒店', description: '爷爷90大寿，四代同堂共38人。', status: 'completed', uploader: '长孙媳', person_count: 38, people_in_photo: [] },
    { id: 7, title: '我小时候和外公', image: null, era: '1990s', scene: 'childhood', source: 'scanned', taken_year: 1995, location: '', description: '', status: 'archived', uploader: '外孙', person_count: 2, people_in_photo: [] },
    { id: 8, title: '2018年清明扫墓', image: null, era: '2010s', scene: 'other', source: 'phone', taken_year: 2018, location: '苏州公墓', description: '家人从各地赶来，祭扫后一起吃了团圆饭。', status: 'annotating', uploader: '堂弟', person_count: 12, people_in_photo: [] },
    { id: 9, title: '奶奶少女时代', image: null, era: '1930s', scene: 'daily_life', source: 'old_album', taken_year: 1938, location: '南京', description: '奶奶说这是她上学时最好的朋友拍的，那年她16岁。', status: 'completed', uploader: '三姑', person_count: 1, people_in_photo: [] },
    { id: 10, title: '年代不详的老照片', image: null, era: 'unknown', scene: 'other', source: 'old_album', taken_year: null, location: '', description: '从旧相册夹层找到的，背面没有字，没人认得出来。', status: 'archived', uploader: '家属', person_count: 4, people_in_photo: [] }
  ]
}

function mockPersons() {
  return [
    { id: 1, name: '李大山', gender: 'M', avatar: null, status: 'confirmed' },
    { id: 2, name: '王秀兰', gender: 'F', avatar: null, status: 'confirmed' },
    { id: 3, name: '李建国', gender: 'M', avatar: null, status: 'confirmed' },
    { id: 4, name: '李建华', gender: 'M', avatar: null, status: 'confirmed' },
    { id: 5, name: '李建梅', gender: 'F', avatar: null, status: 'pending' },
    { id: 6, name: '张桂芬', gender: 'F', avatar: null, status: 'confirmed' },
    { id: 7, name: '李明', gender: 'M', avatar: null, status: 'pending' },
    { id: 8, name: '未知老人', gender: 'U', avatar: null, status: 'pending' }
  ]
}

function mockPeopleInPhoto(photoId) {
  if (photoId === 2) {
    return [
      { id: 11, person: 1, person_detail: { id: 1, name: '李大山', status: 'confirmed' }, person_name_override: '', position_note: '后排中间', old_title: '大山', role_note: '一家之主', added_by: '长孙' },
      { id: 12, person: 2, person_detail: { id: 2, name: '王秀兰', status: 'confirmed' }, person_name_override: '', position_note: '前排中间', old_title: '秀兰', role_note: '', added_by: '长孙' },
      { id: 13, person: null, person_detail: null, person_name_override: '二姑（待确认）', position_note: '前排右一', old_title: '二丫头', role_note: '14岁', added_by: '大姑' }
    ]
  }
  if (photoId === 4) {
    return [
      { id: 21, person: 3, person_detail: { id: 3, name: '李建国', status: 'confirmed' }, person_name_override: '', position_note: '新郎', old_title: '建国', role_note: '28岁', added_by: '三妹' },
      { id: 22, person: 6, person_detail: { id: 6, name: '张桂芬', status: 'confirmed' }, person_name_override: '', position_note: '新娘', old_title: '桂芬', role_note: '25岁', added_by: '三妹' }
    ]
  }
  return []
}
</script>

<style scoped>
.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.era-group-header {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.era-summary {
  background: #fff;
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid var(--border-soft);
  font-size: 13px;
}

.era-label {
  color: var(--text-muted);
  margin-right: 8px;
}

.era-count {
  font-weight: 600;
  color: var(--primary-color);
}

.era-section {
  margin-bottom: 28px;
}

.era-section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--accent-color);
}

.era-section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
}

.photo-detail {
  padding: 8px 0;
}

.detail-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.detail-image-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-image {
  width: 100%;
  aspect-ratio: 4/3;
  background: linear-gradient(135deg, #F5F0E6, #E8D8C4);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-emoji {
  font-size: 80px;
  opacity: 0.6;
}

.photo-emoji.big {
  font-size: 120px;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-info-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-block {
  background: #FFFAF0;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid var(--border-soft);
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid var(--accent-color);
}

.section-content {
  color: var(--text-dark);
  line-height: 1.8;
  font-size: 14px;
}

.empty-note {
  color: var(--text-muted);
  font-size: 13px;
  font-style: italic;
}

.people-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.person-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 10px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid var(--border-soft);
}

.person-info {
  flex: 1;
}

.person-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 6px;
}

.person-name.confirmed {
  color: #059669;
}

.pending-name {
  color: #D97706;
}

.person-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
