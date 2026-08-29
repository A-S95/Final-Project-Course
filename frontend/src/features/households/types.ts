export type HouseholdMember = {
  user_id: string
  name: string
  email: string
  joined_at: string
  is_creator: boolean
}

export type Household = {
  id: string
  name: string
  created_by: string
  created_at: string
  members: HouseholdMember[]
}

export type InviteStatus = 'PENDING' | 'ACCEPTED' | 'DECLINED' | 'CANCELLED'

export type Invite = {
  id: string
  household_id: string
  household_name: string
  invited_user_email: string
  invited_user_name: string
  invited_by_name: string
  status: InviteStatus
  created_at: string
  responded_at: string | null
}
