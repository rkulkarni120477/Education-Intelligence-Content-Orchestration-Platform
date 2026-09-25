/**
 * Phase 5: Workflow Dashboard
 *
 * Main dashboard integrating skill alignment review,
 * recommendations, coverage visualization, and approval workflows.
 */

'use client';

import React, { useState } from 'react';
import { SkillAlignmentReview } from '../SkillMapping/SkillAlignmentReview';
import { RecommendationsDashboard } from '../Recommendations/RecommendationsDashboard';
import { CoverageVisualization } from '../Coverage/CoverageVisualization';

interface WorkflowDashboardProps {
  workflowId: string;
  programName: string;
}

type DashboardTab = 'overview' | 'alignments' | 'recommendations' | 'coverage' | 'accessibility';

export function WorkflowDashboard({ workflowId, programName }: WorkflowDashboardProps) {
  const [activeTab, setActiveTab] = useState<DashboardTab>('overview');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-3xl font-bold text-gray-900">{programName}</h1>
          <p className="text-sm text-gray-600 mt-1">Workflow ID: {workflowId}</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6">
          <nav className="flex gap-8" aria-label="Tabs">
            {[
              { id: 'overview' as const, label: 'Overview' },
              { id: 'alignments' as const, label: 'Skill Alignments' },
              { id: 'recommendations' as const, label: 'Recommendations' },
              { id: 'coverage' as const, label: 'Coverage Analysis' },
              { id: 'accessibility' as const, label: 'Accessibility' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'overview' && <OverviewTab workflowId={workflowId} />}
        {activeTab === 'alignments' && <SkillAlignmentReview workflowId={workflowId} />}
        {activeTab === 'recommendations' && <RecommendationsDashboard workflowId={workflowId} />}
        {activeTab === 'coverage' && <CoverageVisualization workflowId={workflowId} />}
        {activeTab === 'accessibility' && <AccessibilityTab workflowId={workflowId} />}
      </div>
    </div>
  );
}

interface OverviewTabProps {
  workflowId: string;
}

function OverviewTab({ workflowId }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <QuickStatCard
          title="Phase Status"
          value="Phase 5 Review"
          color="blue"
        />
        <QuickStatCard
          title="Next Action"
          value="Approve Alignments"
          color="yellow"
        />
        <QuickStatCard
          title="Estimated Completion"
          value="2-3 Days"
          color="green"
        />
        <QuickStatCard
          title="Critical Issues"
          value="3"
          color="red"
        />
      </div>

      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold mb-4">Workflow Status</h3>
        <div className="space-y-4">
          <StatusStep
            number={1}
            title="Validation"
            status="complete"
            description="Request and access validated"
          />
          <StatusStep
            number={2}
            title="Requirements Extraction"
            status="complete"
            description="Institution requirements extracted via Claude"
          />
          <StatusStep
            number={3}
            title="Course Ingestion"
            status="complete"
            description="Course materials parsed and normalized"
          />
          <StatusStep
            number={4}
            title="Skill Mapping"
            status="complete"
            description="Skills mapped to course content"
          />
          <StatusStep
            number={5}
            title="Review & Approval"
            status="in_progress"
            description="Human review of alignments and recommendations"
          />
          <StatusStep
            number={6}
            title="Final Export"
            status="pending"
            description="Generate final IMSCC/PDF package"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
              Review & Approve Alignments
            </button>
            <button className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700">
              Approve Recommendations
            </button>
            <button className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700">
              Generate Report
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3 text-sm">
            <ActivityItem
              timestamp="2 hours ago"
              action="Skill mapping completed"
              details="25 alignments created"
            />
            <ActivityItem
              timestamp="4 hours ago"
              action="Course ingestion finished"
              details="5 modules extracted"
            />
            <ActivityItem
              timestamp="6 hours ago"
              action="Workflow started"
              details="Requirements extraction initiated"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

interface QuickStatCardProps {
  title: string;
  value: string;
  color: 'blue' | 'yellow' | 'green' | 'red';
}

function QuickStatCard({ title, value, color }: QuickStatCardProps) {
  const bgColor = {
    blue: 'bg-blue-50',
    yellow: 'bg-yellow-50',
    green: 'bg-green-50',
    red: 'bg-red-50',
  }[color];

  const textColor = {
    blue: 'text-blue-700',
    yellow: 'text-yellow-700',
    green: 'text-green-700',
    red: 'text-red-700',
  }[color];

  return (
    <div className={`${bgColor} rounded-lg p-4`}>
      <div className="text-xs text-gray-600 mb-1">{title}</div>
      <div className={`text-lg font-semibold ${textColor}`}>{value}</div>
    </div>
  );
}

interface StatusStepProps {
  number: number;
  title: string;
  status: 'complete' | 'in_progress' | 'pending';
  description: string;
}

function StatusStep({ number, title, status, description }: StatusStepProps) {
  const statusIcon = {
    complete: '✓',
    in_progress: '⟳',
    pending: '○',
  }[status];

  const statusColor = {
    complete: 'text-green-600 bg-green-50',
    in_progress: 'text-blue-600 bg-blue-50',
    pending: 'text-gray-400 bg-gray-50',
  }[status];

  return (
    <div className="flex gap-4">
      <div
        className={`flex items-center justify-center w-10 h-10 rounded-full font-bold text-lg ${statusColor}`}
      >
        {statusIcon}
      </div>
      <div className="flex-1 py-2">
        <div className="font-medium text-gray-900">
          {number}. {title}
        </div>
        <div className="text-sm text-gray-600">{description}</div>
      </div>
    </div>
  );
}

interface ActivityItemProps {
  timestamp: string;
  action: string;
  details: string;
}

function ActivityItem({ timestamp, action, details }: ActivityItemProps) {
  return (
    <div className="border-l-2 border-gray-300 pl-3 py-1">
      <div className="font-medium text-gray-900">{action}</div>
      <div className="text-gray-600">{details}</div>
      <div className="text-gray-500 text-xs">{timestamp}</div>
    </div>
  );
}

interface AccessibilityTabProps {
  workflowId: string;
}

function AccessibilityTab({ workflowId }: AccessibilityTabProps) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Accessibility Audit</h2>

      <div className="bg-white rounded-lg border p-6 space-y-4">
        <div className="grid grid-cols-4 gap-4">
          <StatCard label="Total Findings" value={3} />
          <StatCard label="Critical" value={0} />
          <StatCard label="High" value={1} />
          <StatCard label="Medium" value={2} />
        </div>

        <div className="border-t pt-4">
          <h3 className="font-semibold mb-3">Findings</h3>
          <div className="space-y-3">
            <FindingItem
              severity="high"
              title="Missing alt text on images"
              description="Module 3 contains 5 images without alt text"
              wcagCriteria="WCAG 2.1 1.1.1"
              remediation="Add descriptive alt text to all images"
            />
            <FindingItem
              severity="medium"
              title="Color contrast insufficient"
              description="Some text in the course slides has low contrast ratio"
              wcagCriteria="WCAG 2.1 1.4.3"
              remediation="Increase contrast ratio to at least 4.5:1"
            />
            <FindingItem
              severity="medium"
              title="Missing captions on videos"
              description="3 instructional videos lack captions"
              wcagCriteria="WCAG 2.1 1.2.2"
              remediation="Add captions to all videos"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: number;
}

function StatCard({ label, value }: StatCardProps) {
  return (
    <div className="bg-gray-50 p-3 rounded-lg">
      <div className="text-xs text-gray-600">{label}</div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
    </div>
  );
}

interface FindingItemProps {
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  wcagCriteria: string;
  remediation: string;
}

function FindingItem({
  severity,
  title,
  description,
  wcagCriteria,
  remediation,
}: FindingItemProps) {
  const severityColor = {
    critical: 'bg-red-100 text-red-800 border-red-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200',
  }[severity];

  return (
    <div className={`border rounded-lg p-4 ${severityColor}`}>
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-semibold">{title}</h4>
        <span className="text-xs font-bold uppercase">{severity}</span>
      </div>
      <p className="text-sm mb-2">{description}</p>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="font-medium">WCAG Criteria: </span>
          {wcagCriteria}
        </div>
        <div>
          <span className="font-medium">Remediation: </span>
          {remediation}
        </div>
      </div>
    </div>
  );
}
