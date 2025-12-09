import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/Card';
import { Button } from './ui/Button';
import { searchAPI, SavedDraft } from '../services/api';
import { Trash2, Eye } from 'lucide-react';

const SavedDrafts: React.FC = () => {
  const [drafts, setDrafts] = useState<SavedDraft[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await searchAPI.listDrafts();
      setDrafts(res as SavedDraft[]);
    } catch (e) {
      console.error('Failed to load drafts', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  // Wrapper for browser confirm to satisfy ESLint rule restrictions
  const confirmDelete = (message: string) => {
    // eslint-disable-next-line no-restricted-globals
    return confirm(message);
  };

  const handleDelete = async (id: string) => {
    if (!confirmDelete('Delete this draft?')) return;
    setActionLoading(id);
    try {
      await searchAPI.deleteDraft(id);
      setDrafts(prev => prev.filter(d => d.id !== id));
    } catch (e) {
      console.error('Delete failed', e);
      alert('Failed to delete draft');
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold">Saved Drafts</h1>
        <p className="text-sm text-gray-600">Your previously saved patent drafts</p>
      </div>

      <div className="space-y-4">
        {loading && <div className="text-sm text-gray-500">Loading...</div>}
        {drafts.length === 0 && !loading && (
          <Card>
            <CardContent>
              <div className="text-sm text-gray-600">No saved drafts yet. Save a draft from the Draft Assistant page.</div>
            </CardContent>
          </Card>
        )}

        {drafts.map(d => (
          <Card key={d.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-sm">{d.title || 'Untitled Draft'}</CardTitle>
                  <CardDescription className="text-xs">Saved: {new Date(d.created_at).toLocaleString()}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Button size="sm" onClick={() => setExpandedId(expandedId === d.id ? null : d.id)}>
                    <Eye className="mr-2 h-4 w-4" /> {expandedId === d.id ? 'Hide' : 'View'}
                  </Button>
                  <Button size="sm" variant="destructive" onClick={() => handleDelete(d.id)} disabled={actionLoading === d.id}>
                    <Trash2 className="mr-2 h-4 w-4" /> Delete
                  </Button>
                </div>
              </div>
            </CardHeader>
            {expandedId === d.id && (
              <CardContent>
                <div className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-gray-800">{d.content}</div>
              </CardContent>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
};

export default SavedDrafts;
