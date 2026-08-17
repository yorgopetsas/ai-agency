import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Image, RefreshControl, StyleSheet } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { api, Article } from '../services/api';
import { useNavigation } from '@react-navigation/native';

export default function HomeScreen() {
  const { theme, config } = useTheme();
  const navigation = useNavigation();
  const [articles, setArticles] = useState<Article[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadArticles = async () => {
    try {
      const data = await api.getArticles();
      setArticles(data.slice(0, 10));
    } catch (err) {
      console.warn('Failed to load articles:', err);
    }
  };

  useEffect(() => { loadArticles(); }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadArticles();
    setRefreshing(false);
  };

  const styles = makeStyles(theme);

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>{config.companyName}</Text>
        <Text style={styles.headerSubtitle}>Latest AI News</Text>
      </View>

      {articles.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>No articles yet</Text>
        </View>
      ) : (
        articles.map((article) => (
          <TouchableOpacity
            key={article.id}
            style={styles.card}
            onPress={() => navigation.navigate('ArticleDetail' as never, { article } as never)}
          >
            {article.image_url ? (
              <Image source={{ uri: article.image_url }} style={styles.cardImage} />
            ) : null}
            <View style={styles.cardBody}>
              <Text style={styles.cardTitle} numberOfLines={2}>{article.headline}</Text>
              <Text style={styles.cardOverview} numberOfLines={2}>{article.overview}</Text>
              <View style={styles.cardMeta}>
                <Text style={styles.cardDate}>{article.date_formatted}</Text>
                {article.provider ? <Text style={styles.cardProvider}>{article.provider}</Text> : null}
              </View>
            </View>
          </TouchableOpacity>
        ))
      )}
    </ScrollView>
  );
}

function makeStyles(theme: any) {
  return StyleSheet.create({
    container: { flex: 1, backgroundColor: theme.colors.background },
    header: { padding: theme.spacing.lg, paddingTop: 60, backgroundColor: theme.colors.primary },
    headerTitle: { fontSize: 28, fontWeight: 'bold', color: '#fff' },
    headerSubtitle: { fontSize: 16, color: '#fff', opacity: 0.8, marginTop: 4 },
    empty: { padding: 40, alignItems: 'center' },
    emptyText: { color: theme.colors.textMuted, fontSize: 16 },
    card: { backgroundColor: theme.colors.card, marginHorizontal: theme.spacing.md, marginTop: theme.spacing.md, borderRadius: theme.borderRadius, overflow: 'hidden', elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.1, shadowRadius: 3 },
    cardImage: { width: '100%', height: 180 },
    cardBody: { padding: theme.spacing.md },
    cardTitle: { fontSize: 18, fontWeight: '600', color: theme.colors.text, marginBottom: 6 },
    cardOverview: { fontSize: 14, color: theme.colors.textSecondary, lineHeight: 20 },
    cardMeta: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 10 },
    cardDate: { fontSize: 12, color: theme.colors.textMuted },
    cardProvider: { fontSize: 12, color: theme.colors.primary },
  });
}
