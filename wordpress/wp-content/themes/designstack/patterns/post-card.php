<?php
/**
 * Title: Карточка подборки
 * Slug: designstack/post-card
 * Categories: designstack
 * Inserter: no
 *
 * Подборка — запись, а не ресурс: без логотипа, меток и кнопки (h7). Варианты для архивов дайджеста и обзоров
 * добавит этап 13 вместе с самими архивами.
 *
 * @package designstack
 */

$ds_posts = array(
	array( 'Бесплатный набор для прототипирования', 'Редактор, UI-кит и уроки, чтобы собрать первый кликабельный прототип без платных тарифов', '8 ресурсов · 5&nbsp;сен 2026' ),
	array( 'Шрифты с кириллицей для интерфейса', 'Десять бесплатных шрифтов, у которых кириллица нарисована, а не дорисована', '10 ресурсов · 29&nbsp;авг 2026' ),
	array( 'Чем заменить Figma из России', 'Что теряете и что выигрываете с Pixso, Penpot и Lunacy, если платный тариф оплатить нельзя', '6 ресурсов · 22&nbsp;авг 2026' ),
);

?>
<!-- wp:html -->
<div class="ds-post-list">
	<?php foreach ( $ds_posts as $ds_post ) : ?>
	<article class="ds-post-card">
		<h3 class="ds-post-card__title"><a class="ds-post-card__link" href="/collections/free-prototyping/"><?php echo esc_html( $ds_post[0] ); ?></a></h3>
		<p class="ds-post-card__desc"><?php echo esc_html( $ds_post[1] ); ?></p>
		<p class="ds-meta ds-post-card__meta"><?php echo wp_kses_post( $ds_post[2] ); ?></p>
	</article>
	<?php endforeach; ?>
</div>
<!-- /wp:html -->
