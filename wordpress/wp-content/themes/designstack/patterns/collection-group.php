<?php
/**
 * Title: Группа ресурсов в подборке
 * Slug: designstack/collection-group
 * Categories: designstack
 *
 * Куратор вставляет группу в запись подборки (c3): заголовок, строка описания и список ресурсов.
 * Список — тот же паттерн; на этапе 12 его место займёт блок «список ресурсов» с выбором записей.
 *
 * @package designstack
 */

?>
<!-- wp:group {"className":"ds-section"} -->
<div class="wp-block-group ds-section"><!-- wp:group {"className":"ds-section__head"} -->
<div class="wp-block-group ds-section__head"><!-- wp:heading {"className":"ds-section__title"} -->
<h2 class="wp-block-heading ds-section__title">Схема экранов</h2>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"ds-section__sub"} -->
<p class="ds-section__sub">Набросать экраны и переходы до макета</p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<!-- wp:group {"className":"ds-section__body"} -->
<div class="wp-block-group ds-section__body"><!-- wp:pattern {"slug":"designstack/resource-list"} /--></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
