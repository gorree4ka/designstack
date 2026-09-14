<?php
/**
 * Title: Подвал сайта
 * Slug: designstack/site-footer
 * Categories: designstack
 * Inserter: no
 *
 * Подписка, ссылки, 12 тем и копирайт (brief §6, D35). Кнопки «Подписаться» нет, пока не создан канал (US-43, O5):
 * её выведет этап 12 по адресу канала в настройках.
 *
 * @package designstack
 */

$ds_topics = array(
	'UX-исследования'       => 'ux-research',
	'Прототипирование'      => 'prototyping',
	'UI и визуал'           => 'ui-visual',
	'Типографика'           => 'typography',
	'Иконки и иллюстрации'  => 'icons-illustrations',
	'Дизайн-системы'        => 'design-systems',
	'AI для дизайнера'      => 'ai-for-designers',
	'Аналитика и метрики'   => 'analytics-metrics',
	'Карьера и портфолио'   => 'career-portfolio',
	'Доступность'           => 'accessibility',
	'Мобильный дизайн'      => 'mobile-design',
	'Веб и лендинги'        => 'web-landings',
);

$ds_links = array(
	'Обзоры'             => '/reviews/',
	'Принципы оценки'    => '/about/#principles',
	'Предложить ресурс'  => '/suggest/',
	'Политика данных'    => '/privacy/',
);

?>
<!-- wp:group {"className":"ds-footer","layout":{"type":"constrained"}} -->
<div class="wp-block-group ds-footer"><!-- wp:group {"align":"wide","className":"ds-footer__inner"} -->
<div class="wp-block-group alignwide ds-footer__inner"><!-- wp:html -->
<div class="ds-footer__subscribe">
	<p class="ds-footer__title">Дайджест раз в неделю</p>
	<p class="ds-meta">Кнопка «Подписаться» появится вместе с каналом</p>
</div>
<ul class="ds-footer__links">
	<?php foreach ( $ds_links as $ds_title => $ds_url ) : ?>
	<li><a class="ds-link" href="<?php echo esc_url( $ds_url ); ?>"><?php echo esc_html( $ds_title ); ?></a></li>
	<?php endforeach; ?>
</ul>
<nav class="ds-footer__topics" aria-label="Темы">
	<p class="ds-footer__title">Темы</p>
	<ul>
		<?php foreach ( $ds_topics as $ds_title => $ds_slug ) : ?>
		<li><a class="ds-link" href="/topic/<?php echo esc_attr( $ds_slug ); ?>/"><?php echo esc_html( $ds_title ); ?></a></li>
		<?php endforeach; ?>
	</ul>
</nav>
<p class="ds-footer__copy">© 2026 DesignStack</p>
<!-- /wp:html --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
