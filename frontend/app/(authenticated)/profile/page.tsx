'use client'

import React from 'react'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import { useUserProfile } from '@/lib/api/profile'

const formatDate = (value: string | null) => {
  if (!value) return 'Not provided'
  const [year, month, day] = value.split('-').map(Number)
  return new Date(Date.UTC(year, month - 1, day)).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  })
}

export default function PersonalInformationPage() {
  const { isAuthenticated } = useAuthRequired()
  const profileQuery = useUserProfile()

  if (!isAuthenticated) return null

  const profile = profileQuery.data
  const details = profile ? [
    ['First Name', profile.first_name],
    ['Last Name', profile.last_name],
    ['Age', profile.age?.toString()],
    ['Email', profile.email],
    ['Date of Birth', formatDate(profile.date_of_birth)],
    ['City', profile.city],
    ['State', profile.state],
    ['Country', profile.country],
    ['Address', profile.address],
    ['ZIP', profile.zip_code],
    ['Mobile Number', profile.mobile_number],
  ] : []

  return (
    <section className="max-w-3xl space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-ink">Personal Information</h1>
        <p className="mt-2 text-ink-muted">Your account and contact details</p>
      </header>

      {profileQuery.isLoading && <p role="status">Loading personal information...</p>}
      {profileQuery.isError && (
        <p role="alert" className="text-error">Unable to load personal information.</p>
      )}

      {profile && profile.id && (
        <div className="flex items-center gap-6 rounded-lg bg-surface border border-border p-6">
          <img
            src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/users/profile/photo/${profile.id}`}
            alt={profile.full_name || 'Profile'}
            className="w-24 h-24 rounded-full border-2 border-primary object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none'
            }}
          />
          <div>
            <h2 className="text-xl font-semibold text-ink">
              {profile.full_name || profile.first_name || 'User'}
            </h2>
            <p className="text-sm text-ink-muted">{profile.email}</p>
            {profile.mobile_number && (
              <p className="text-sm text-ink-muted">{profile.mobile_number}</p>
            )}
          </div>
        </div>
      )}

      {profile && (
        <dl className="divide-y divide-border border-y border-border">
          {details.map(([label, value]) => (
            <div key={label} className="grid grid-cols-1 gap-1 py-4 sm:grid-cols-[12rem_1fr] sm:gap-4">
              <dt className="text-sm font-medium text-ink-muted">{label}</dt>
              <dd className="break-words text-sm text-ink">{value || 'Not provided'}</dd>
            </div>
          ))}
        </dl>
      )}
    </section>
  )
}