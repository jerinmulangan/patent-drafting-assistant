import React, { useState } from 'react';
import { Bell, Shield, Key, Users, Globe, Database } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';

const preferenceGroups = [
  {
    title: 'Notifications',
    description: 'Control the cadence and channels for workflow events.',
    icon: Bell,
    toggles: [
      { label: 'Search completions', description: 'Send a ping when long-running searches finish' },
      { label: 'Draft exports', description: 'Alert me when a teammate exports a draft' },
      { label: 'Weekly analytics brief', description: 'Digest of novelty deltas, trends, and alerts' },
    ],
  },
  {
    title: 'Security',
    description: 'Strengthen workspace access and audit policies.',
    icon: Shield,
    toggles: [
      { label: 'Require MFA', description: 'Enforce time-based OTP for all collaborators' },
      { label: 'Session alerts', description: 'Email me when a new device signs in' },
      { label: 'Download approvals', description: 'Gate raw data exports behind review' },
    ],
  },
  {
    title: 'Integrations',
    description: 'Wire PatentAI into your downstream systems.',
    icon: Globe,
    toggles: [
      { label: 'Slack webhooks', description: 'Stream high-priority alerts into #ip-scouting' },
      { label: 'Jira automations', description: 'Open tickets when blocking prior art arrives' },
      { label: 'Drive sync', description: 'Mirror final drafts to your document hub' },
    ],
  },
];

const apiKeys = [
  { name: 'Production', key: 'pk_live_8f0e••••••72a3', scopes: ['search', 'draft', 'analytics'], status: 'Active' },
  { name: 'Staging', key: 'pk_test_19bd••••••ea0f', scopes: ['search', 'draft'], status: 'Active' },
  { name: 'Legacy CLI', key: 'pk_live_e21c••••••aa90', scopes: ['search'], status: 'Revoking' },
];

const collaborators = [
  { name: 'Maya Ortiz', role: 'Lead Counsel', status: 'Owner' },
  { name: 'Ravi Shah', role: 'Patent Analyst', status: 'Editor' },
  { name: 'Claire Ngu', role: 'AI Specialist', status: 'Editor' },
  { name: 'Jordan Lee', role: 'Reviewer', status: 'Viewer' },
];

const Settings: React.FC = () => {
  const [toggles, setToggles] = useState<Record<string, boolean>>(() =>
    preferenceGroups.reduce((acc, group) => {
      group.toggles.forEach((toggle) => {
        acc[`${group.title}-${toggle.label}`] = true;
      });
      return acc;
    }, {} as Record<string, boolean>),
  );

  const handleToggle = (id: string) => {
    setToggles((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="page-padding space-y-8">
      <div className="grid gap-6 lg:grid-cols-3">
        {preferenceGroups.map((group) => {
          const Icon = group.icon;
          return (
            <Card key={group.title}>
              <CardHeader className="flex items-start justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Icon className="h-5 w-5 text-slate-400" />
                    {group.title}
                  </CardTitle>
                  <CardDescription>{group.description}</CardDescription>
                </div>
                <Badge variant="outline">Live</Badge>
              </CardHeader>
              <CardContent className="space-y-4">
                {group.toggles.map((toggle) => {
                  const id = `${group.title}-${toggle.label}`;
                  return (
                    <div key={id} className="flex items-start justify-between rounded-2xl border border-slate-100 p-4">
                      <div>
                        <p className="text-sm font-semibold text-slate-900">{toggle.label}</p>
                        <p className="text-sm text-slate-500">{toggle.description}</p>
                      </div>
                      <button
                        onClick={() => handleToggle(id)}
                        className={`relative h-6 w-11 rounded-full transition-all ${
                          toggles[id] ? 'bg-emerald-400' : 'bg-slate-200'
                        }`}
                        aria-pressed={toggles[id]}
                        type="button"
                      >
                        <span
                          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                            toggles[id] ? 'translate-x-5' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5 text-slate-400" />
                API Keys
              </CardTitle>
              <CardDescription>Rotate and scope programmatic access.</CardDescription>
            </div>
            <Button size="sm">Generate Key</Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {apiKeys.map((key) => (
              <div
                key={key.name}
                className="rounded-2xl border border-slate-100 bg-white/60 p-4 shadow-sm ring-1 ring-white/60 backdrop-blur"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{key.name}</p>
                    <p className="text-xs text-slate-500">{key.key}</p>
                  </div>
                  <Badge variant="outline">{key.status}</Badge>
                </div>
                <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
                  {key.scopes.map((scope) => (
                    <span key={scope} className="rounded-full bg-slate-100 px-3 py-1 font-medium">
                      {scope}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-slate-400" />
                Collaborators
              </CardTitle>
              <CardDescription>Manage access, roles, and invitations.</CardDescription>
            </div>
            <Button size="sm" variant="outline">
              Invite
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {collaborators.map((person) => (
              <div key={person.name} className="flex items-center justify-between rounded-2xl border border-slate-100 p-4">
                <div>
                  <p className="text-sm font-semibold text-slate-900">{person.name}</p>
                  <p className="text-xs text-slate-500">{person.role}</p>
                </div>
                <Badge variant="secondary">{person.status}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-slate-400" />
              Data Residency
            </CardTitle>
            <CardDescription>Choose the jurisdiction for indexing and storage.</CardDescription>
          </div>
          <Button size="sm" variant="outline">
            Request Change
          </Button>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          {['United States (primary)', 'Canada', 'Germany'].map((region) => (
            <div key={region} className="rounded-2xl border border-slate-100 bg-white/70 p-4 text-sm">
              <p className="font-semibold text-slate-900">{region}</p>
              <p className="text-xs text-slate-500">Low latency • GDPR compliant</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;
