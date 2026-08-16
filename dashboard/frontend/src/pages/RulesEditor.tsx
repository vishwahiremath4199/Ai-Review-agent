import { useEffect, useState } from 'react';
import apiClient, { RuleSet } from '../api/client';

export default function RulesEditor() {
  const [ruleset, setRuleset] = useState<RuleSet | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getRules();
      setRuleset(data);
      setError('');
    } catch (err: any) {
      setError('Failed to load rules');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!ruleset) return;

    try {
      setIsSaving(true);
      setError('');
      setSuccess('');

      // Validate rules first
      await apiClient.validateRules(ruleset);

      // Save rules
      await apiClient.updateRules(ruleset);
      setSuccess('Rules saved successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save rules');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddRule = () => {
    if (!ruleset) return;
    ruleset.rules.push({
      match: '**/*.ts',
      category: 'code-quality',
      checks: ['Add checks here'],
    });
    setRuleset({ ...ruleset });
  };

  const handleDeleteRule = (index: number) => {
    if (!ruleset) return;
    ruleset.rules.splice(index, 1);
    setRuleset({ ...ruleset });
  };

  const handleUpdateRule = (
    index: number,
    field: keyof typeof ruleset.rules[0],
    value: any
  ) => {
    if (!ruleset) return;
    ruleset.rules[index] = { ...ruleset.rules[index], [field]: value };
    setRuleset({ ...ruleset });
  };

  const handleAddCheck = (ruleIndex: number) => {
    if (!ruleset) return;
    ruleset.rules[ruleIndex].checks.push('New check');
    setRuleset({ ...ruleset });
  };

  const handleDeleteCheck = (ruleIndex: number, checkIndex: number) => {
    if (!ruleset) return;
    ruleset.rules[ruleIndex].checks.splice(checkIndex, 1);
    setRuleset({ ...ruleset });
  };

  const handleUpdateCheck = (
    ruleIndex: number,
    checkIndex: number,
    value: string
  ) => {
    if (!ruleset) return;
    ruleset.rules[ruleIndex].checks[checkIndex] = value;
    setRuleset({ ...ruleset });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!ruleset) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error || 'Failed to load rules'}
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Review Rules Editor</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
          {success}
        </div>
      )}

      {/* General Instructions */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">General Instructions</h2>
        <textarea
          value={ruleset.general_instructions}
          onChange={(e) =>
            setRuleset({ ...ruleset, general_instructions: e.target.value })
          }
          rows={6}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Rules */}
      <div className="space-y-6 mb-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-800">Rules ({ruleset.rules.length})</h2>
          <button
            onClick={handleAddRule}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg"
          >
            + Add Rule
          </button>
        </div>

        {ruleset.rules.map((rule, ruleIndex) => (
          <div key={ruleIndex} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">Rule {ruleIndex + 1}</h3>
              <button
                onClick={() => handleDeleteRule(ruleIndex)}
                className="text-red-600 hover:text-red-700 font-medium text-sm"
              >
                Delete
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  File Pattern (e.g., **/auth/**)
                </label>
                <input
                  type="text"
                  value={rule.match}
                  onChange={(e) =>
                    handleUpdateRule(ruleIndex, 'match', e.target.value)
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  value={rule.category}
                  onChange={(e) =>
                    handleUpdateRule(ruleIndex, 'category', e.target.value)
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option>security</option>
                  <option>database</option>
                  <option>code-quality</option>
                  <option>frontend</option>
                  <option>testing</option>
                  <option>bug-risk</option>
                  <option>style</option>
                </select>
              </div>
            </div>

            {/* Checks */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Checks ({rule.checks.length})
                </label>
                <button
                  onClick={() => handleAddCheck(ruleIndex)}
                  className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                >
                  + Add Check
                </button>
              </div>
              <div className="space-y-2">
                {rule.checks.map((check, checkIndex) => (
                  <div key={checkIndex} className="flex gap-2">
                    <input
                      type="text"
                      value={check}
                      onChange={(e) =>
                        handleUpdateCheck(ruleIndex, checkIndex, e.target.value)
                      }
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={() => handleDeleteCheck(ruleIndex, checkIndex)}
                      className="text-red-600 hover:text-red-700 font-medium"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={handleSave}
        disabled={isSaving}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-lg text-lg"
      >
        {isSaving ? 'Saving...' : 'Save Rules'}
      </button>
    </div>
  );
}
