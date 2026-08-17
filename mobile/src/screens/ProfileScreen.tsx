import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Alert, StyleSheet } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { api, User } from '../services/api';
import { useNavigation } from '@react-navigation/native';

export default function ProfileScreen() {
  const { theme, config } = useTheme();
  const navigation = useNavigation();
  const [user, setUser] = useState<User | null>(null);
  const [usage, setUsage] = useState<Record<string, any>>({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const u = await api.getUser();
      setUser(u);
      if (u?.client_id) {
        const usageData = await api.getUsage(u.client_id);
        setUsage(usageData);
      }
    } catch (err) {
      console.warn('Failed to load profile:', err);
    }
  };

  const handleLogout = async () => {
    Alert.alert('Logout', 'Are you sure?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Logout',
        style: 'destructive',
        onPress: async () => {
          await api.clearAuth();
          navigation.reset({ index: 0, routes: [{ name: 'Login' as never }] });
        },
      },
    ]);
  };

  const styles = makeStyles(theme);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{user?.name?.charAt(0) || '?'}</Text>
        </View>
        <Text style={styles.name}>{user?.name || 'Guest'}</Text>
        <Text style={styles.email}>{user?.email || ''}</Text>
        {user?.client_id ? <Text style={styles.clientId}>Client: {user.client_id}</Text> : null}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Usage</Text>
        {Object.entries(usage).length === 0 ? (
          <Text style={styles.emptyText}>No usage data</Text>
        ) : (
          Object.entries(usage).map(([key, data]: [string, any]) => (
            <View key={key} style={styles.usageRow}>
              <Text style={styles.usageLabel}>{key.replace(/_/g, ' ')}</Text>
              <View style={styles.usageBar}>
                <View style={[styles.usageFill, { width: `${Math.min(data.percentage || 0, 100)}%` }]} />
              </View>
              <Text style={styles.usageValue}>{data.used} / {data.limit}</Text>
            </View>
          ))
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('ChangePassword' as never)}>
          <Text style={styles.menuText}>Change Password</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem} onPress={() => navigation.navigate('Settings' as never)}>
          <Text style={styles.menuText}>Settings</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function makeStyles(theme: any) {
  return StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    header: { alignItems: 'center', padding: theme.spacing.xl, paddingTop: 60, backgroundColor: theme.colors.primary },
    avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: 'rgba(255,255,255,0.2)', justifyContent: 'center', alignItems: 'center' },
    avatarText: { fontSize: 32, color: '#fff', fontWeight: 'bold' },
    name: { fontSize: 22, fontWeight: 'bold', color: '#fff', marginTop: 12 },
    email: { fontSize: 14, color: '#fff', opacity: 0.8, marginTop: 4 },
    clientId: { fontSize: 12, color: '#fff', opacity: 0.6, marginTop: 4 },
    section: { marginTop: theme.spacing.md, paddingHorizontal: theme.spacing.md },
    sectionTitle: { fontSize: 18, fontWeight: '600', color: theme.colors.text, marginBottom: 12 },
    emptyText: { color: theme.colors.textMuted, fontSize: 14 },
    usageRow: { marginBottom: 16 },
    usageLabel: { fontSize: 14, color: theme.colors.textSecondary, textTransform: 'capitalize', marginBottom: 6 },
    usageBar: { height: 8, backgroundColor: theme.colors.border, borderRadius: 4, overflow: 'hidden' },
    usageFill: { height: '100%', backgroundColor: theme.colors.primary, borderRadius: 4 },
    usageValue: { fontSize: 12, color: theme.colors.textMuted, marginTop: 4 },
    menuItem: { padding: 16, backgroundColor: theme.colors.card, borderRadius: theme.borderRadius, marginBottom: 8 },
    menuText: { fontSize: 16, color: theme.colors.text },
    logoutButton: { margin: theme.spacing.lg, padding: 16, backgroundColor: theme.colors.error, borderRadius: theme.borderRadius, alignItems: 'center', marginBottom: 40 },
    logoutText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  });
}
