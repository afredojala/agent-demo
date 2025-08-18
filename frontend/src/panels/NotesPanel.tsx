import React from 'react';

interface Note {
  id: string;
  body: string;
  created_at: string;
}

const NotesPanel: React.FC = () => {
  const [notes, setNotes] = React.useState<Note[]>([]);

  React.useEffect(() => {
    setNotes([
      { id: '1', body: 'Initial investigation shows authentication service is down', created_at: '2024-01-15T12:30:00Z' },
      { id: '2', body: 'Escalated to infrastructure team', created_at: '2024-01-15T16:30:00Z' },
      { id: '3', body: 'Follow-up: issue resolved, monitoring for stability', created_at: '2024-01-16T09:00:00Z' },
    ]);
  }, []);

  return (
    <div className="col-span-2 border p-3 rounded bg-white shadow">
      <h3 className="font-semibold mb-3">Notes Panel</h3>
      <div className="space-y-2 max-h-40 overflow-y-auto">
        {notes.map(note => (
          <div key={note.id} className="text-sm p-2 bg-gray-50 rounded">
            <div className="text-gray-800">{note.body}</div>
            <div className="text-xs text-gray-500 mt-1">
              {new Date(note.created_at).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3">
        <textarea 
          className="w-full p-2 border rounded text-sm"
          placeholder="Add a note..."
          rows={2}
        />
        <button className="mt-2 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">
          Add Note
        </button>
      </div>
    </div>
  );
};

export default NotesPanel;