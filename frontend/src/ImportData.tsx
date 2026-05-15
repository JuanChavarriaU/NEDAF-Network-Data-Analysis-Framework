import { useState } from 'react';
import { Database, File, AlertCircle, CheckCircle2, Loader2, FolderOpen } from 'lucide-react';
import { DataManagementAPI, handleApiError } from './services/api';

export function ImportData() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleLoadData = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!file) return;

    try {
      setIsLoading(true);
      setError(null);
      setSuccessMsg(null);

      const res = await DataManagementAPI.loadData(file);
      setSuccessMsg(`Dataset loaded successfully! Columns: ${res.columns.length}, Rows: ${res.rows}`);

    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setSuccessMsg(null);
    }
  };

  return (
    <div className="flex flex-col h-full animate-fade-in fade-in zoom-in duration-300">
      <header className="glass-panel mb-6 p-5">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Database className="text-brand-400" />
          Import Data
        </h1>
        <p className="text-sm text-gray-400 mt-1">Connect to local datasets to begin analysis.</p>
      </header>

      <div className="flex-1 glass-panel flex flex-col items-center justify-center p-10 relative overflow-hidden">
        {/* Decorative background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand-500/10 blur-3xl rounded-full pointer-events-none" />

        <div className="w-24 h-24 rounded-full bg-dark-bg border border-dark-border flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(var(--color-brand-500),0.15)] relative z-10">
          <File size={40} className="text-brand-400" />
        </div>

        <h2 className="text-2xl font-semibold text-white mb-2 relative z-10">Load Local Dataset</h2>
        <p className="text-gray-400 text-center max-w-md mb-8 relative z-10">
          Upload your dataset (CSV, JSON, Parquet, GML, MTX) from your local machine.
        </p>

        <form onSubmit={handleLoadData} className="w-full max-w-lg relative z-10">
          <div className="flex flex-col gap-4">
            <div className="relative flex flex-col gap-2">
              <label className="flex items-center justify-between w-full bg-dark-bg border border-dark-border hover:border-brand-500 rounded-xl py-4 px-5 cursor-pointer transition-all group">
                <div className="flex items-center gap-3 truncate">
                  <FolderOpen className="text-brand-400 shrink-0" size={24} />
                  <span className="text-gray-300 truncate font-medium">
                    {file ? file.name : "Click to select a file..."}
                  </span>
                </div>
                <span className="text-sm text-gray-500 group-hover:text-brand-400 transition-colors ml-4 shrink-0">
                  Browse Files
                </span>
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                  accept=".csv,.json,.parquet,.gml,.mtx"
                />
              </label>
              {file && (
                <div className="text-xs text-gray-500 ml-2">
                  Size: {(file.size / 1024 / 1024).toFixed(2)} MB
                </div>
              )}
            </div>

            {error && (
              <div className="flex items-start gap-2 text-red-400 bg-red-400/10 border border-red-400/20 p-3 rounded-lg text-sm animate-in slide-in-from-top-2">
                <AlertCircle size={18} className="shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}

            {successMsg && (
              <div className="flex items-start gap-2 text-green-400 bg-green-400/10 border border-green-400/20 p-3 rounded-lg text-sm animate-in slide-in-from-top-2">
                <CheckCircle2 size={18} className="shrink-0 mt-0.5" />
                <p>{successMsg}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !file}
              className="w-full flex items-center justify-center gap-2 py-3 bg-brand-600 hover:bg-brand-500 disabled:bg-brand-600/50 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all shadow-lg shadow-brand-900/50 hover:shadow-brand-500/25 mt-2"
            >
              {isLoading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Loading...
                </>
              ) : (
                'Load Dataset'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
