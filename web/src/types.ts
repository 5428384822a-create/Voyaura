export interface MapStats {
  lit_cities: number
  memories: number
  photos: number
  vlog_minutes: number
}

export interface VisitedCity {
  adcode: string
  name_zh: string
  name_en: string
  province_zh: string
  longitude: number
  latitude: number
  first_visited_at: string
  last_visited_at: string
  memory_count: number
  check_in_source: 'device' | 'ip' | 'manual'
}

export interface MapYearCityActivity {
  adcode: string
  memory_count: number
}

export interface MapYearSummary {
  year: number
  stats: MapStats
  cities: MapYearCityActivity[]
}

export interface MapOverview {
  username: string
  map_center: [number, number]
  default_zoom: number
  stats: MapStats
  visited_cities: VisitedCity[]
  year_summaries: MapYearSummary[]
}

export interface CheckInCoordinates {
  username: string
  longitude: number
  latitude: number
  accuracy_meters: number | null
  coordinate_system: 'WGS84'
}

export interface ManualCityCheckIn {
  username: string
  adcode: string
  city_name: string
  province_name: string
  longitude: number
  latitude: number
  source: 'ip' | 'manual'
}

export interface CityCandidate {
  adcode: string
  city_name: string
  province_name: string
  longitude: number
  latitude: number
  source: 'ip' | 'manual'
}

export interface CheckInPreview {
  adcode: string
  city_name: string
  province_name: string
  city_center: [number, number]
  map_position: [number, number]
  formatted_address: string
  accuracy_meters: number | null
  already_lit: boolean
  location_source: 'device' | 'ip' | 'manual'
  privacy_notice: string
}

export interface CheckInConfirmResult {
  status: 'created' | 'updated'
  city: VisitedCity
}

export interface PoiSearchDraft {
  keywords: string
  city_adcode: string
  category: string
  page: number
  page_size: number
}

export interface PoiItem {
  id: string
  name: string
  category: string
  typecode: string
  address: string
  province: string
  city: string
  district: string
  adcode: string
  longitude: number
  latitude: number
  coordinate_system: 'GCJ02'
  telephone: string | null
  rating: string | null
  average_cost: string | null
  opening_hours: string | null
  navigation_url: string
}

export interface PoiSearchResult {
  keywords: string
  city_adcode: string
  total: number
  page: number
  page_size: number
  items: PoiItem[]
  provider: 'amap'
  queried_at: string
}

export interface PoiDetailResult {
  item: PoiItem
  provider: 'amap'
  queried_at: string
}

export type LocalRouteMode = 'walking' | 'transit' | 'driving'
export type IntercityRouteMode = 'train' | 'high_speed_rail' | 'flight'

export interface RouteCoordinate {
  longitude: number
  latitude: number
}

export interface LocalRouteDraft {
  mode: LocalRouteMode
  origin: RouteCoordinate
  destination: RouteCoordinate
  origin_adcode: string
  destination_adcode: string
}

export interface RouteStep {
  instruction: string
  distance_meters: number
  duration_seconds: number | null
  road_name: string | null
  transport: string
}

export interface RouteOption {
  distance_meters: number
  duration_seconds: number
  walking_distance_meters: number | null
  tolls_yuan: number | null
  taxi_cost_yuan: number | null
  steps: RouteStep[]
}

export interface LocalRouteResult {
  mode: LocalRouteMode
  origin: RouteCoordinate
  destination: RouteCoordinate
  coordinate_system: 'GCJ02'
  provider: 'amap'
  queried_at: string
  options: RouteOption[]
}

export interface RouteProviderCapability {
  mode: LocalRouteMode | IntercityRouteMode
  provider: string
  available: boolean
  state: 'available' | 'configuration_required' | 'partner_required'
  data_scope: string[]
  application_url: string | null
  notice: string
}

export interface RouteCapabilities {
  local: RouteProviderCapability[]
  intercity: RouteProviderCapability[]
  queried_at: string
}

export type XiaoxiPartyType = 'solo' | 'couple' | 'friends' | 'family_children' | 'older_adults' | 'unspecified'
export type XiaoxiPace = 'relaxed' | 'balanced' | 'rich' | 'unspecified'
export type XiaoxiTransportMode = 'walking' | 'transit' | 'driving' | 'taxi'
export type XiaoxiSearchCategory = 'culture_history' | 'museum_art' | 'nature_scenery' | 'photography' | 'family' | 'food' | 'shopping' | 'nightlife' | 'neighborhood' | 'other'

export interface XiaoxiPlanningIntent {
  city_name: string | null
  day_count: number | null
  party_type: XiaoxiPartyType
  pace: XiaoxiPace
  interests: string[]
  must_visit_names: string[]
  avoid_names: string[]
  dietary_constraints: string[]
  transport_modes: XiaoxiTransportMode[]
  daily_start_time: string | null
  daily_end_time: string | null
  total_budget_yuan: number | null
}

export interface XiaoxiPlanningContext extends Partial<XiaoxiPlanningIntent> {
  city_adcode?: string | null
}

export interface XiaoxiPlanningPreviewDraft {
  username?: string
  message: string
  context?: XiaoxiPlanningContext
}

export interface XiaoxiPlanningCapability {
  provider: 'deepseek'
  model: string
  available: boolean
  state: 'available' | 'configuration_required'
  structured_output: true
  notice: string
}

export interface XiaoxiAttractionHypothesis {
  name: string
  category: XiaoxiSearchCategory
  reason: string
  priority: number
}

export interface XiaoxiPoiSearchTheme {
  keyword: string
  category: XiaoxiSearchCategory
  reason: string
  desired_count: number
}

export interface XiaoxiPlanningPreview {
  status: 'needs_clarification' | 'ready_for_poi_search'
  assistant_message: string
  requirements: XiaoxiPlanningIntent
  city_adcode: string | null
  missing_fields: string[]
  clarification_questions: string[]
  candidate_target_count: number
  recommended_daily_attractions: { min: number, max: number }
  attraction_hypotheses: XiaoxiAttractionHypothesis[]
  search_themes: XiaoxiPoiSearchTheme[]
  assumptions: string[]
  warnings: string[]
  provider: 'deepseek'
  model: string
  generated_at: string
}

export interface MemoryMediaAsset {
  id: string
  kind: 'photo' | 'vlog'
  original_filename: string
  mime_type: string
  width: number | null
  height: number | null
  duration_seconds: number | null
  visibility: 'private'
  upload_status: 'ready'
  exif_status: 'removed' | 'not_applicable'
  scan_status: 'clean' | 'not_scanned'
  thumbnail_url: string | null
  content_url: string | null
  thumbnail_width: number | null
  thumbnail_height: number | null
  created_at: string
}

export interface CityMemoryItem {
  id: string
  title: string
  body: string | null
  occurred_at: string
  visibility: 'private' | 'shared'
  media: MemoryMediaAsset[]
}

export interface CityMemoryDetail {
  city: VisitedCity
  visit_note: string | null
  stats: {
    memories: number
    photos: number
    vlogs: number
    vlog_minutes: number
  }
  memories: CityMemoryItem[]
}

export interface NewMemoryInput {
  title: string
  body: string | null
  occurred_at: string
  visibility: 'private' | 'shared'
}

export interface CityMemoryDraft extends NewMemoryInput {
  username: string
  client_request_id: string
}

export interface CityMemoryPreview extends NewMemoryInput {
  city_adcode: string
  city_name: string
  confirmation_notice: string
}

export interface CityMemoryConfirmResult {
  status: 'created' | 'existing'
  memory: CityMemoryItem
}

export interface CityMemoryUpdatePreview extends CityMemoryPreview {
  memory_id: string
}

export interface CityMemoryUpdateConfirmResult {
  status: 'updated' | 'existing'
  memory: CityMemoryItem
}

export interface CityMemoryDeleteDraft {
  username: string
  client_request_id: string
}

export interface CityMemoryDeletePreview {
  memory_id: string
  city_adcode: string
  city_name: string
  title: string
  occurred_at: string
  media_count: number
  confirmation_notice: string
}

export interface CityMemoryDeleteConfirmResult {
  status: 'deleted' | 'existing'
  memory_id: string
  city_adcode: string
}

export interface MediaUploadDraft {
  username: string
  client_request_id: string
  kind: 'photo' | 'vlog'
  filename: string
  mime_type: string
  byte_size: number
  visibility: 'private'
}

export interface MediaUploadPreview {
  kind: 'photo' | 'vlog'
  filename: string
  mime_type: string
  byte_size: number
  quota_remaining_bytes: number
  visibility: 'private'
  confirmation_notice: string
}

export interface MediaUploadIntent {
  status: 'created' | 'existing'
  asset_id: string
  upload_url: string
  method: 'PUT'
  required_headers: Record<string, string>
  expires_at: string
}

export interface MediaUploadProgress {
  loaded: number
  total: number
  percent: number
}

export interface MediaUploadCompleteResult {
  status: 'processing' | 'ready' | 'existing'
  asset_id: string
  asset: MemoryMediaAsset | null
  processing_notice: string
}

export interface MediaProcessingStatus {
  status: 'pending' | 'processing' | 'ready' | 'failed'
  asset_id: string
  scan_status: 'not_scanned' | 'pending' | 'scanning' | 'clean' | 'infected' | 'error'
  failure_code: string | null
  failure_message: string | null
  retryable: boolean
  asset: MemoryMediaAsset | null
}

export interface MediaTaskItem {
  asset_id: string
  memory_id: string
  memory_title: string
  kind: 'photo' | 'vlog'
  original_filename: string
  byte_size: number
  upload_status: 'pending' | 'processing' | 'failed'
  scan_status: 'not_scanned' | 'pending' | 'scanning' | 'clean' | 'infected' | 'error'
  failure_code: string | null
  failure_message: string | null
  retryable: boolean
  expired: boolean
  upload_expires_at: string | null
  created_at: string
}

export interface MediaTaskList {
  items: MediaTaskItem[]
}

export interface MediaDeleteDraft {
  username: string
  client_request_id: string
}

export interface MediaDeletePreview {
  asset_id: string
  memory_id: string
  city_adcode: string
  city_name: string
  memory_title: string
  kind: 'photo' | 'vlog'
  original_filename: string
  byte_size: number
  upload_status: 'pending' | 'ready' | 'failed'
  confirmation_notice: string
}

export interface MediaDeleteConfirmResult {
  status: 'deleted' | 'existing'
  asset_id: string
  memory_id: string
  city_adcode: string
}

export type ImagePreservationLevel = 'balanced' | 'high'
export type ImageCaptionLayout = 'archive_band' | 'postcard_corner' | 'vertical_stamp'
export type ImageCaptionPalette = 'coral' | 'forest' | 'ink'
export type ImageCaptionFontStyle = 'sans' | 'serif'

export interface ImageStyleRecipe {
  version: string
  aspect_ratio: string
  layout: string
  focal_element: string
  typography: string
  color: string
  texture: string
  default_preservation: ImagePreservationLevel
  preservation_level: ImagePreservationLevel | null
}

export interface ImageStyleSource {
  name: string
  version: string
  url: string
  license: string
}

export interface ImageCaption {
  title: string
  location: string
  date: string
  layout: ImageCaptionLayout
  palette: ImageCaptionPalette
  font_style: ImageCaptionFontStyle
}

export interface XiaoxiPhotoCapability {
  available: boolean
  missing_settings: string[]
  asset_version: string | null
  positions: Array<'left' | 'right'>
  scales: Array<'small' | 'medium' | 'large'>
  poses: string[]
  expressions: string[]
}

export interface ImageCompanion {
  asset_version: string | null
  pose: string
  expression: string
  position: 'left' | 'right'
  scale: 'small' | 'medium' | 'large'
  method: string
  disclosure: string
}

export interface ImageStyle {
  id: string
  name: string
  description: string
  swatch: string
  recipe: ImageStyleRecipe
  source: ImageStyleSource | null
}

export interface ImageStyleCatalog {
  provider: string
  available: boolean
  missing_settings: string[]
  styles: ImageStyle[]
  companion: XiaoxiPhotoCapability
}

export interface ImageJobDraft {
  username: string
  source_asset_id: string
  style_id: string
  prompt: string
  negative_prompt: string | null
  preservation_level: ImagePreservationLevel
  caption_mode: 'none' | 'travel_stamp'
  caption_layout: ImageCaptionLayout
  caption_palette: ImageCaptionPalette
  caption_font_style: ImageCaptionFontStyle
  companion_enabled: boolean
  companion_position: 'left' | 'right'
  companion_scale: 'small' | 'medium' | 'large'
}

export interface ImageJobCreateDraft extends ImageJobDraft {
  client_request_id: string
}

export interface ImageJobPreview {
  source_asset_id: string
  source_filename: string
  city_adcode: string
  city_name: string
  memory_id: string
  memory_title: string
  style: ImageStyle
  recipe: ImageStyleRecipe
  effective_prompt: string
  negative_prompt: string
  preservation_level: ImagePreservationLevel
  caption_mode: 'none' | 'travel_stamp'
  caption: ImageCaption | null
  companion: ImageCompanion | null
  companion_available: boolean
  companion_missing_settings: string[]
  provider: string
  provider_available: boolean
  confirmation_notice: string
}

export interface ImageJob {
  id: string
  status: 'queued' | 'running' | 'succeeded' | 'failed'
  source_asset_id: string
  source_filename: string
  source_url: string | null
  source_thumbnail_url: string | null
  city_adcode: string
  city_name: string
  memory_id: string
  memory_title: string
  style_id: string
  provider: string
  provider_job_id: string | null
  prompt: string
  negative_prompt: string | null
  preservation_level: ImagePreservationLevel
  recipe: ImageStyleRecipe
  style_source: ImageStyleSource | null
  model_names: string[]
  caption_mode: 'none' | 'travel_stamp'
  caption: ImageCaption | null
  companion: ImageCompanion | null
  is_favorite: boolean
  output_url: string | null
  download_url: string | null
  output_mime_type: string | null
  output_width: number | null
  output_height: number | null
  failure_code: string | null
  failure_message: string | null
  retryable: boolean
  created_at: string
  completed_at: string | null
}

export interface ImageJobCreateResult {
  status: 'created' | 'existing'
  job: ImageJob
}

export interface ImageJobList {
  items: ImageJob[]
}

export interface ImageJobDeleteDraft {
  username?: string
  client_request_id: string
}

export interface ImageJobDeletePreview {
  job_id: string
  source_filename: string
  city_name: string
  memory_title: string
  style: ImageStyle
  status: ImageJob['status']
  has_output: boolean
  confirmation_notice: string
}

export interface ImageJobDeleteResult {
  status: 'deleted' | 'existing'
  job_id: string
}

export interface AppErrorInfo {
  code: string
  message: string
  details: Record<string, unknown>
  retryable: boolean
  requestId?: string
}

export type TripStatus = 'draft' | 'confirmed' | 'planning' | 'ready' | 'archived'

export interface TripCreateDraft {
  username?: string
  client_request_id: string
  title: string
  origin_city_name?: string | null
  origin_city_adcode?: string | null
  destination_city_name: string
  destination_city_adcode: string
  start_date?: string | null
  day_count: number
  timezone?: string
  party_type?: XiaoxiPartyType
  pace?: XiaoxiPace
  interests?: string[]
  transport_modes?: XiaoxiTransportMode[]
  dietary_constraints?: string[]
  total_budget_yuan?: string | null
  daily_start_time?: string | null
  daily_end_time?: string | null
  requirements_snapshot?: Record<string, unknown>
}

export interface MealSuggestion {
  id: string
  stop_id: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  cuisine_tags: string[]
  recommended_dishes: string[]
  budget_yuan: string | null
  dietary_match: 'unknown' | 'matched' | 'partial' | 'conflict'
  reservation_status: 'unknown' | 'not_required' | 'recommended' | 'required'
  created_at: string
  updated_at: string
}

export interface ItineraryStop {
  id: string
  trip_day_id: string
  sequence: number
  kind: 'attraction' | 'meal' | 'lodging' | 'activity'
  name: string
  poi_id: string | null
  category: string | null
  address: string | null
  longitude: number | null
  latitude: number | null
  coordinate_system: 'GCJ02' | null
  start_time: string | null
  end_time: string | null
  suggested_duration_minutes: number | null
  opening_status: 'unknown' | 'open' | 'closed' | 'needs_verification'
  opening_hours: string | null
  ticket_price_yuan: string | null
  recommendation_reason: string | null
  verification_status: 'unverified' | 'verified' | 'ambiguous' | 'not_found'
  status: 'planned' | 'confirmed' | 'skipped'
  source_queried_at: string | null
  meal_suggestion: MealSuggestion | null
  created_at: string
  updated_at: string
}

export interface TransferLeg {
  id: string
  trip_day_id: string
  sequence: number
  from_stop_id: string
  to_stop_id: string
  mode: 'walking' | 'transit' | 'driving' | 'taxi' | 'cycling' | 'train' | 'flight'
  provider: string | null
  distance_meters: number | null
  duration_seconds: number | null
  walking_distance_meters: number | null
  estimated_cost_yuan: string | null
  verification_status: 'estimated' | 'verified' | 'failed'
  queried_at: string | null
  route_snapshot: Record<string, unknown> | null
  created_at: string
}

export interface TripDay {
  id: string
  trip_id: string
  day_number: number
  travel_date: string | null
  title: string | null
  theme: string | null
  lodging_area: string | null
  status: 'draft' | 'planned' | 'confirmed'
  start_time: string | null
  end_time: string | null
  budget_yuan: string | null
  walking_intensity: 'unknown' | 'low' | 'moderate' | 'high'
  weather_snapshot: Record<string, unknown> | null
  stops: ItineraryStop[]
  transfer_legs: TransferLeg[]
  created_at: string
  updated_at: string
}

export interface ItineraryEvidence {
  id: string
  trip_id: string
  stop_id: string | null
  meal_suggestion_id: string | null
  transfer_leg_id: string | null
  evidence_type: 'poi' | 'route' | 'opening_hours' | 'ticket' | 'weather' | 'recommendation'
  provider: string
  external_id: string | null
  source_name: string
  source_url: string | null
  source_title: string | null
  queried_at: string
  confidence_status: 'unverified' | 'verified' | 'conflicting'
  value_snapshot: Record<string, unknown>
  usage_note: string | null
  created_at: string
}

export interface TripSummary {
  id: string
  username: string
  title: string
  status: TripStatus
  origin_city_name: string | null
  origin_city_adcode: string | null
  destination_city_name: string
  destination_city_adcode: string
  start_date: string | null
  end_date: string | null
  day_count: number
  timezone: string
  party_type: XiaoxiPartyType
  pace: XiaoxiPace
  interests: string[]
  transport_modes: XiaoxiTransportMode[]
  total_budget_yuan: string | null
  created_at: string
  updated_at: string
}

export interface TripDetail extends TripSummary {
  dietary_constraints: string[]
  daily_start_time: string | null
  daily_end_time: string | null
  requirements_snapshot: Record<string, unknown>
  confirmed_at: string | null
  days: TripDay[]
  evidence: ItineraryEvidence[]
}

export interface TripCreateResult {
  status: 'created' | 'existing'
  trip: TripDetail
}

export interface TripList {
  items: TripSummary[]
  total: number
  limit: number
  offset: number
}

export interface MapIssue {
  code: string
  message: string
  suggestion: string
}

export type AppView = 'map' | 'journeys' | 'memories' | 'studio' | 'profile'
