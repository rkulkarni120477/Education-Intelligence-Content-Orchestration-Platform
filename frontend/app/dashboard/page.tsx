'use client'

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-[#1E40AF] to-[#0F172A] text-white p-8 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold mb-2">Welcome to Academian Education</h1>
        <p className="text-[#F5DEB3] text-lg">Accelerate course and content development with AI-powered workflows</p>
      </div>


      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold text-[#0F172A] mb-4">⚡ Quick Actions</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <button className="bg-[#1E40AF] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#0F172A] transition">
            ➕ New Course
          </button>
          <button className="bg-[#1E40AF] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#0F172A] transition">
            📤 Upload Content
          </button>
          <button className="bg-[#1E40AF] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#0F172A] transition">
            📊 View Reports
          </button>
          <button className="bg-[#1E40AF] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#0F172A] transition">
            🔧 Configure Workflow
          </button>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-[#FFFFFF] rounded-lg border-2 border-[#3B82F6] p-6">
        <h3 className="text-lg font-bold text-[#0F172A] mb-4">🟢 System Status</h3>
        <div className="space-y-2 text-sm text-[#1E40AF]">
          <p>✅ Frontend: Running on localhost:3001</p>
          <p>✅ Backend API: Running on localhost:8000</p>
          <p>✅ Database: SQLite connected</p>
          <p>✅ AWS IAM: Integration pending</p>
        </div>
      </div>
    </div>
  )
}
