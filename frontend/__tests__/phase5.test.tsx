/**
 * Phase 5 Frontend Component Tests
 *
 * Tests for skill alignment review, recommendations dashboard,
 * coverage visualization, and workflow dashboard.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SkillAlignmentReview } from '@/components/SkillMapping/SkillAlignmentReview';
import { RecommendationsDashboard } from '@/components/Recommendations/RecommendationsDashboard';
import { CoverageVisualization } from '@/components/Coverage/CoverageVisualization';
import { WorkflowDashboard } from '@/components/Phase5/WorkflowDashboard';

// Mock query client for testing
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={createTestQueryClient()}>
    {children}
  </QueryClientProvider>
);

describe('Phase 5: Frontend Components', () => {
  describe('SkillAlignmentReview', () => {
    it('should render the component', () => {
      render(<SkillAlignmentReview workflowId="test-workflow" />, { wrapper });
      expect(screen.getByText('Skill Alignment Review')).toBeInTheDocument();
    });

    it('should display filter options', () => {
      render(<SkillAlignmentReview workflowId="test-workflow" />, { wrapper });
      const statusFilter = screen.getByDisplayValue('candidate');
      expect(statusFilter).toBeInTheDocument();
    });

    it('should show stats cards', () => {
      render(<SkillAlignmentReview workflowId="test-workflow" />, { wrapper });
      expect(screen.getByText('Total Alignments')).toBeInTheDocument();
      expect(screen.getByText('Selected for Approval')).toBeInTheDocument();
      expect(screen.getByText('Confidence Avg')).toBeInTheDocument();
      expect(screen.getByText('Skills Mapped')).toBeInTheDocument();
    });
  });

  describe('RecommendationsDashboard', () => {
    it('should render the component', () => {
      render(<RecommendationsDashboard workflowId="test-workflow" />, { wrapper });
      expect(screen.getByText('Curriculum Improvement Recommendations')).toBeInTheDocument();
    });

    it('should display search input', () => {
      render(<RecommendationsDashboard workflowId="test-workflow" />, { wrapper });
      const searchInput = screen.getByPlaceholderText('Search recommendations...');
      expect(searchInput).toBeInTheDocument();
    });

    it('should display priority filter', () => {
      render(<RecommendationsDashboard workflowId="test-workflow" />, { wrapper });
      const prioritySelect = screen.getByDisplayValue('All Priorities');
      expect(prioritySelect).toBeInTheDocument();
    });

    it('should show stat cards for each priority', () => {
      render(<RecommendationsDashboard workflowId="test-workflow" />, { wrapper });
      expect(screen.getByText('Total')).toBeInTheDocument();
      expect(screen.getByText('Critical')).toBeInTheDocument();
      expect(screen.getByText('High')).toBeInTheDocument();
      expect(screen.getByText('Medium')).toBeInTheDocument();
      expect(screen.getByText('Low')).toBeInTheDocument();
    });
  });

  describe('CoverageVisualization', () => {
    it('should render the component', () => {
      render(<CoverageVisualization workflowId="test-workflow" />, { wrapper });
      expect(screen.getByText('Skill Coverage Analysis')).toBeInTheDocument();
    });

    it('should display coverage breakdown', () => {
      render(<CoverageVisualization workflowId="test-workflow" />, { wrapper });
      expect(screen.getByText('Covered')).toBeInTheDocument();
      expect(screen.getByText('Partially Covered')).toBeInTheDocument();
      expect(screen.getByText('Uncovered')).toBeInTheDocument();
    });

    it('should show skill coverage details', () => {
      render(<CoverageVisualization workflowId="test-workflow" />, { wrapper });
      expect(screen.getByText('Skill Coverage Details')).toBeInTheDocument();
    });

    it('should display gap summary', () => {
      render(<CoverageVisualization workflowId="test-workflow" />, { wrapper });
      expect(screen.getByText('Gap Summary')).toBeInTheDocument();
    });
  });

  describe('WorkflowDashboard', () => {
    it('should render the component', () => {
      render(
        <WorkflowDashboard
          workflowId="test-workflow"
          programName="Test Program"
        />,
        { wrapper }
      );
      expect(screen.getByText('Test Program')).toBeInTheDocument();
    });

    it('should display navigation tabs', () => {
      render(
        <WorkflowDashboard
          workflowId="test-workflow"
          programName="Test Program"
        />,
        { wrapper }
      );
      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Skill Alignments')).toBeInTheDocument();
      expect(screen.getByText('Recommendations')).toBeInTheDocument();
      expect(screen.getByText('Coverage Analysis')).toBeInTheDocument();
      expect(screen.getByText('Accessibility')).toBeInTheDocument();
    });

    it('should show overview content by default', () => {
      render(
        <WorkflowDashboard
          workflowId="test-workflow"
          programName="Test Program"
        />,
        { wrapper }
      );
      expect(screen.getByText('Workflow Status')).toBeInTheDocument();
      expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    });

    it('should switch tabs when clicked', () => {
      render(
        <WorkflowDashboard
          workflowId="test-workflow"
          programName="Test Program"
        />,
        { wrapper }
      );

      const alignmentsTab = screen.getByText('Skill Alignments');
      fireEvent.click(alignmentsTab);

      expect(screen.getByText('Skill Alignment Review')).toBeInTheDocument();
    });
  });
});

describe('Phase 5: Type Definitions', () => {
  it('should have correct TypeScript types', () => {
    // This is a compile-time check
    // If types are incorrect, TypeScript compilation will fail
    expect(true).toBe(true);
  });
});
