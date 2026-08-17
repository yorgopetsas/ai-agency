import React, { useState } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity, Alert, StyleSheet } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { api } from '../services/api';
import { useNavigation } from '@react-navigation/native';

export default function SettingsScreen() {
  const { theme, config, refresh } = useTheme();
  const navigation = useNavigation();
  const [serverUrl, setServerUrl] = useState(config.apiBaseUrl);
  const [clientId, setClientId] = useState(config.clientId);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.setBaseUrl(serverUrl);
      await refresh(clientId, serverUrl);
      Alert.alert('Saved', 'Settings updated');
    } catch (err) {
      Alert.alert('Error', 'Failed to save settings');
    }
    setSaving(false);
  };

  const styles = makeStyles(theme);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Settings</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Server</Text>
        <Text style={styles.label}>Server URL</Text>
        <TextInput
          style={styles.input}
          value={serverUrl}
          onChangeText={setServerUrl}
          placeholder="http://localhost:5001"
          autoCapitalize="none"
          autoCorrect={false}
        />

        <Text style={styles.label}>Client ID</Text>
        <TextInput
          style={styles.input}
          value={clientId}
          onChangeText={setClientId}
          placeholder="internal"
          autoCapitalize="none"
          autoCorrect={false}
        />

        <TouchableOpacity style={styles.saveButton} onPress={handleSave} disabled={saving}>
          <Text style={styles.saveButtonText}>{saving ? 'Saving...' : 'Save'}</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>App Version</Text>
          <Text style={styles.infoValue}>1.0.0</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Company</Text>
          <Text style={styles.infoValue}>{config.companyName}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Theme</Text>
          <View style={[styles.themePreview, { backgroundColor: theme.colors.primary }]} />
        </View>
      </View>

      <TouchableOpacity style={styles.dangerButton} onPress={() => {
        Alert.alert('Reset', 'Clear all data?', [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Reset', style: 'destructive', onPress: async () => { await api.clearAuth(); } },
        ]);
      }}>
        <Text style={styles.dangerText}>Reset App Data</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function makeStyles(theme: any) {
  return StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    header: { padding: theme.spacing.lg, paddingTop: 60, backgroundColor: theme.colors.primary },
    headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#fff' },
    section: { marginTop: theme.spacing.md, paddingHorizontal: theme.spacing.md },
    sectionTitle: { fontSize: 18, fontWeight: '600', color: theme.colors.text, marginBottom: 12 },
    label: { fontSize: 14, color: theme.colors.textSecondary, marginBottom: 6 },
    input: { backgroundColor: theme.colors.card, borderWidth: 1, borderColor: theme.colors.border, borderRadius: theme.borderRadius, padding: 14, fontSize: 16, color: theme.colors.text, marginBottom: 16 },
    saveButton: { backgroundColor: theme.colors.primary, padding: 16, borderRadius: theme.borderRadius, alignItems: 'center' },
    saveButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
    infoRow: { flexDirection: 'row', justifyContent: 'space-between', padding: 14, backgroundColor: theme.colors.card, borderRadius: theme.borderRadius, marginBottom: 8 },
    infoLabel: { fontSize: 14, color: theme.colors.textSecondary },
    infoValue: { fontSize: 14, color: theme.colors.text },
    themePreview: { width: 20, height: 20, borderRadius: 10 },
    dangerButton: { margin: theme.spacing.lg, padding: 16, borderWidth: 1, borderColor: theme.colors.error, borderRadius: theme.borderRadius, alignItems: 'center', marginBottom: 40 },
    dangerText: { color: theme.colors.error, fontSize: 16 },
  });
}
