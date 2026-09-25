'use client'

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-[#8B5A3C] to-[#6B4423] text-white p-8 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold mb-2">Welcome to Academian Education</h1>
        <p className="text-[#F5DEB3] text-lg">Accelerate course and content development with AI-powered workflows</p>
      </div>


      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold text-[#6B4423] mb-4">⚡ Quick Actions</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <button className="bg-[#8B5A3C] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#6B4423] transition">
            ➕ New Course
          </button>
          <button className="bg-[#8B5A3C] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#6B4423] transition">
            📤 Upload Content
          </button>
          <button className="bg-[#8B5A3C] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#6B4423] transition">
            📊 View Reports
          </button>
          <button className="bg-[#8B5A3C] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#6B4423] transition">
            🔧 Configure Workflow
          </button>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-[#FFF8F0] rounded-lg border-2 border-[#D2B48C] p-6">
        <h3 className="text-lg font-bold text-[#6B4423] mb-4">🟢 System Status</h3>
        <div className="space-y-2 text-sm text-[#8B5A3C]">
          <p>✅ Frontend: Running on localhost:3001</p>
          <p>✅ Backend API: Running on localhost:8000</p>
          <p>✅ Database: SQLite connected</p>
          <p>✅ AWS IAM: Integration pending</p>
        </div>
      </div>
    </div>
  )
}
