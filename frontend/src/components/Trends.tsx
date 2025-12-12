import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { ArrowUpRight, Flame, Target, Activity, Layers, Compass } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Badge } from './ui/Badge';

const trendData = [
  { month: 'Jan', quantum: 20, biotech: 12, robotics: 15 },
  { month: 'Feb', quantum: 28, biotech: 15, robotics: 18 },
  { month: 'Mar', quantum: 35, biotech: 18, robotics: 21 },
  { month: 'Apr', quantum: 42, biotech: 25, robotics: 24 },
  { month: 'May', quantum: 55, biotech: 28, robotics: 27 },
  { month: 'Jun', quantum: 63, biotech: 32, robotics: 31 },
];

const intensityData = [
  { label: 'Quantum Cryptography', score: 92, field: 'QIS' },
  { label: 'Neuromorphic Chips', score: 85, field: 'Semiconductors' },
  { label: 'AI Drug Discovery', score: 80, field: 'BioTech' },
  { label: 'Autonomous Swarms', score: 74, field: 'Robotics' },
];

const flightPlans = [
  {
    title: 'Quantum Communications',
    focus: 'Secure entanglement routing for space-ground relays',
    status: 'Accelerating',
    signal: '+38% QoQ',
    icon: Compass,
  },
  {
    title: 'Regenerative Biofabrication',
    focus: 'AI-grown implantables and adaptive tissue scaffolds',
    status: 'Emerging',
    signal: '+22% QoQ',
    icon: Target,
  },
  {
    title: 'Swarm Autonomy',
    focus: 'Collective sensor fusion for defense and logistics',
    status: 'Stabilizing',
    signal: '+11% QoQ',
    icon: Layers,
  },
];

const Trends: React.FC = () => {
  return (
    <div className="page-padding space-y-8">
      <div className="rounded-3xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-800 p-8 text-white shadow-[0_25px_60px_rgba(2,6,23,0.35)]">
        <div className="flex flex-wrap items-center justify-between gap-6">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-white/60">Signal Observatory</p>
            <h1 className="mt-3 text-3xl font-semibold">Technology Trends Radar</h1>
            <p className="mt-2 text-sm text-white/70">
              Live intelligence across emerging innovation corridors, updated hourly from patent filings, grant notices, and citation velocity.
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-right">
            <p className="text-sm uppercase tracking-[0.3em] text-white/60">Signal Momentum</p>
            <p className="mt-3 text-4xl font-semibold text-emerald-300">+64%</p>
            <p className="text-xs text-white/60">vs. previous quarter</p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {[
          { title: 'New filings this week', value: '128', delta: '+14%', icon: ArrowUpRight },
          { title: 'Active frontier topics', value: '42', delta: '+6', icon: Flame },
          { title: 'Live alert rules', value: '19', delta: '3 critical', icon: Activity },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardContent className="space-y-4 p-6">
                <div className="flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{stat.title}</p>
                  <Icon className="h-5 w-5 text-slate-400" />
                </div>
                <p className="text-3xl font-semibold text-slate-900">{stat.value}</p>
                <p className="text-sm text-emerald-500">{stat.delta}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="pb-0">
            <CardTitle className="text-xl">Focus Area Velocity</CardTitle>
            <CardDescription>Rolling six-month patent signal intensity</CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <XAxis dataKey="month" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip />
                  <Line type="monotone" dataKey="quantum" stroke="#22d3ee" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="biotech" stroke="#a855f7" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="robotics" stroke="#f59e0b" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-xl">Signal Intensity</CardTitle>
            <CardDescription>Highest novelty velocity by cluster</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 pt-6">
            {intensityData.map((item) => (
              <div key={item.label} className="space-y-2 rounded-2xl border border-slate-100 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold">{item.label}</p>
                    <p className="text-xs text-slate-500">{item.field}</p>
                  </div>
                  <Badge variant="secondary">{item.score}</Badge>
                </div>
                <div className="h-2 rounded-full bg-slate-100">
                  <div className="h-2 rounded-full bg-gradient-to-r from-sky-400 to-indigo-500" style={{ width: `${item.score}%` }} />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-xl">Trajectory Forecast</CardTitle>
            <CardDescription>Projected filings vs. existing art</CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="colorQuantum" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="month" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip />
                  <Area type="monotone" dataKey="quantum" stroke="#0ea5e9" fillOpacity={1} fill="url(#colorQuantum)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {flightPlans.map((plan) => {
            const Icon = plan.icon;
            return (
              <Card key={plan.title}>
                <CardContent className="flex flex-col gap-3 p-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-900/5">
                        <Icon className="h-5 w-5 text-slate-500" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-slate-900">{plan.title}</p>
                        <p className="text-xs text-slate-500">{plan.focus}</p>
                      </div>
                    </div>
                    <Badge variant="outline">{plan.status}</Badge>
                  </div>
                  <p className="text-sm font-semibold text-emerald-500">{plan.signal}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Trends;
