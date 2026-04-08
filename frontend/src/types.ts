export interface NotificationSub {
  enabled: boolean
  signin: boolean
  problem: boolean
  call: boolean
  danmu: boolean
  red_packet: boolean
}

export interface CourseItem {
  classroom_id: string
  name: string
  teacher_name: string | null
  active: boolean
}
